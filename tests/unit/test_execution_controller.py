"""Analytical execution schedules, accepted boundaries, and bound continuation."""
from dataclasses import FrozenInstanceError, replace

import pytest

from otqa import (
    AlgorithmPolicy, AnsweredQuery, ExecutionCursor, Problem, Query, QueryBudget,
    SingleCandidateStop, SolveContinuation, continuation_from_result,
)
from otqa.errors import (
    AnswerProviderError, InputValidationError, NumericalError, PlanningInvariantError,
    RecorderError,
)
from otqa.execution import initial_cursor, resolve_cycle, validate_cursor
from otqa.models import QueryCounts, StateAnalysis
from otqa.models.execution import HorizonSelectionEvidence, PlanningAttempt, ProgressEvidence
from otqa.models.planning import FixedScore, PlanningDecision, QueryEvaluation
from otqa.solver import _drive


PROBLEM = Problem(((1., 0.), (0., 1.), (.6, .6)))
HISTORY = (AnsweredQuery(Query(0, 1, 0.), '>'),)


def policy(depth=3, *, mode='countdown', threshold=.001):
    return AlgorithmPolicy('fixed', depth, 'both', 3, 'candidate_count', SingleCandidateStop(),
                           mode, min_expected_progress=threshold)


def selection(config, depth, *, outcome='available'):
    if outcome == 'no_query':
        horizon = HorizonSelectionEvidence(depth, 0, 0, outcome)
        return PlanningAttempt(depth, (depth,), outcome, horizon_evidence=(horizon,))
    terminal = 2. if outcome == 'available' else 3. - .0005
    progress = ProgressEvidence('candidate_count', 3., terminal, 3. - terminal,
                                config.min_expected_progress,
                                admissible=outcome == 'available')
    query = Query(0, 1, 1. + depth / 10)
    decision = PlanningDecision(query, depth, FixedScore(terminal, terminal, (terminal,)),
                                (('<', .5), ('=', 0.), ('>', .5)), QueryEvaluation(query, terminal, ()))
    admitted = decision if outcome == 'available' else None
    evidence = progress if admitted else None
    horizon = HorizonSelectionEvidence(depth, 1, 1, outcome, admitted, evidence, decision, progress)
    return PlanningAttempt(depth, (depth,), outcome, admitted, evidence, decision, (horizon,))


class ScheduledPlanner:
    def __init__(self, config, *, end_after=4, outcomes=None, advance_error=None):
        self.config, self.end_after = config, end_after
        self.outcomes = outcomes or {}
        self.advance_error = advance_error
        self.calls, self.closed = [], False

    def initial_state(self, history):
        return tuple(history)

    def analyze(self, state, *, volumes):
        candidates = (0,) if len(state) >= self.end_after else (0, 1, 2)
        return StateAnalysis(len(state), candidates, tuple((i, 1. / len(candidates)) for i in candidates),
                             tuple((i, 1. / len(candidates)) for i in candidates))

    def plan(self, state, *, requested_depth):
        address = len(state), requested_depth
        self.calls.append(address)
        outcome = self.outcomes.get(address, 'available')
        if isinstance(outcome, BaseException):
            raise outcome
        return selection(self.config, requested_depth, outcome=outcome)

    def advance(self, state, answer):
        if self.advance_error is not None:
            raise self.advance_error
        return state + (answer,)

    def close(self):
        self.closed = True


def run(planner, *, history=(), cursor=None, provider=lambda query: '>', recorder=None,
        budget=QueryBudget()):
    return _drive(PROBLEM, planner.config, provider, budget=budget, history=history,
                  recorder=recorder, observer=None, session=planner, execution_cursor=cursor)


@pytest.mark.parametrize('outcome', ['no_query', 'insufficient_expected_progress'])
@pytest.mark.parametrize('remaining', [1, 2])
def test_early_full_retry_resets_block_and_preserves_every_attempt(outcome, remaining):
    config = policy()
    planner = ScheduledPlanner(config, outcomes={(1, remaining): outcome})
    result = run(planner, history=HISTORY, cursor=ExecutionCursor(1, remaining))
    assert planner.calls == [(1, remaining), (1, 3), (2, 2), (3, 1)]
    assert result.exactly_solved and result.query_counts == QueryCounts(1, 3, 3, 4)
    assert [record.planning.horizon for record in result.queries] == [3, 2, 1]
    first = result.planning_cycles[0]
    assert first.restart_reason == outcome and len(first.attempts) == 2
    assert first.proposed_cursor_after_answer == ExecutionCursor(2, 2)
    assert result.execution_cursor == ExecutionCursor(4, 3)
    assert result.queries[0].cycle is first


@pytest.mark.parametrize('final', ['no_query', 'insufficient_expected_progress'])
def test_full_retry_failure_is_terminal_and_never_loops(final):
    config = policy()
    planner = ScheduledPlanner(config, outcomes={(1, 1): 'no_query', (1, 3): final})
    result = run(planner, history=HISTORY, cursor=ExecutionCursor(1, 1))
    assert result.termination_reason == final and not result.solved
    assert planner.calls == [(1, 1), (1, 3)]
    assert result.query_counts == QueryCounts(1, 0, 0, 1)
    assert result.execution_cursor == ExecutionCursor(1, 1)
    assert result.planning_cycles[0].proposed_cursor_after_answer is None


@pytest.mark.parametrize('depth', [1, 3])
@pytest.mark.parametrize('mode', ['countdown', 'receding'])
def test_rejection_at_full_depth_never_repeats_identical_request(depth, mode):
    config = policy(depth, mode=mode)
    planner = ScheduledPlanner(config, outcomes={(0, depth): 'no_query'})
    assert run(planner).termination_reason == 'no_query'
    assert planner.calls == [(0, depth)]


def test_warmstart_uses_full_depth_instead_of_history_modulo():
    planner = ScheduledPlanner(policy(), end_after=2)
    result = run(planner, history=HISTORY)
    assert planner.calls == [(1, 3)]
    assert result.execution_cursor == ExecutionCursor(2, 2)


def test_answer_budget_prevents_even_a_shortened_failed_plan():
    planner = ScheduledPlanner(policy())
    result = run(planner, history=HISTORY, cursor=ExecutionCursor(1, 1), budget=QueryBudget(1))
    assert result.termination_reason == 'max_questions'
    assert planner.calls == [] and result.planning_cycles == ()


def test_provider_failure_never_consumes_the_new_block_or_exports_unanswered_dispatch():
    planner = ScheduledPlanner(policy(), outcomes={(1, 1): 'no_query'})
    with pytest.raises(AnswerProviderError) as caught:
        run(planner, history=HISTORY, cursor=ExecutionCursor(1, 1), provider=lambda query: 1 / 0)
    context = caught.value.context
    assert context.execution_cursor == ExecutionCursor(1, 1)
    assert context.query_counts == QueryCounts(1, 1, 0, 1)
    assert context.planning_cycles[-1].restart_reason == 'no_query'
    with pytest.raises(InputValidationError, match='unanswered dispatch'):
        continuation_from_result(PROBLEM, planner.config, context)


def test_accepted_answer_before_failed_followup_analysis_is_exportable_with_new_phase():
    config = policy()
    planner = ScheduledPlanner(config, outcomes={(1, 1): 'no_query'}, advance_error=RuntimeError('geometry'))
    observed = []
    with pytest.raises(NumericalError) as caught:
        run(planner, history=HISTORY, cursor=ExecutionCursor(1, 1), recorder=observed.append)
    context = caught.value.context
    assert context.execution_cursor == ExecutionCursor(2, 2)
    assert context.open_query is not None and len(context.queries) == 0
    assert context.query_counts == QueryCounts(1, 1, 1, 2)
    assert observed[-1].execution_cursor == context.execution_cursor
    resumed = continuation_from_result(PROBLEM, config, context)
    assert resumed.answers == context.answers and resumed.execution_cursor == ExecutionCursor(2, 2)
    with pytest.raises(InputValidationError, match='different problem or policy'):
        continuation_from_result(PROBLEM, replace(config, grid_size=5), context)


def test_public_sdk_continuation_keeps_post_restart_phase_while_warmstart_resets(monkeypatch):
    import otqa
    import otqa.planning
    config = policy()
    failed = ScheduledPlanner(config, outcomes={(1, 1): 'no_query'}, advance_error=RuntimeError('geometry'))
    with pytest.raises(NumericalError) as caught:
        run(failed, history=HISTORY, cursor=ExecutionCursor(1, 1))
    checkpoint = continuation_from_result(PROBLEM, config, caught.value.context)
    continued = ScheduledPlanner(config, end_after=3)
    monkeypatch.setattr(otqa.planning, 'PlannerSession', lambda *args: continued)
    result = otqa.solve(PROBLEM, config, lambda query: '>', continuation=checkpoint)
    assert continued.calls == [(2, 2)]
    assert result.execution_cursor == ExecutionCursor(3, 1)
    warmed = ScheduledPlanner(config, end_after=3)
    monkeypatch.setattr(otqa.planning, 'PlannerSession', lambda *args: warmed)
    result = otqa.solve(PROBLEM, config, lambda query: '>', initial_answers=checkpoint.answers)
    assert warmed.calls == [(2, 3)]
    assert result.execution_cursor == ExecutionCursor(3, 2)


def test_failed_answer_recorder_has_memory_cursor_without_claiming_a_durable_one():
    planner = ScheduledPlanner(policy(), end_after=1)
    confirmed = []

    def recorder(event):
        if type(event).__name__ == 'AnswerReceived':
            raise OSError('fsync failed')
        confirmed.append(event)

    with pytest.raises(RecorderError) as caught:
        run(planner, recorder=recorder)
    assert caught.value.context.execution_cursor == ExecutionCursor(1, 2)
    assert caught.value.context.query_counts.answered_total == 1
    assert not any(type(event).__name__ == 'AnswerReceived' for event in confirmed)
    assert planner.closed


def test_failed_replacement_retains_completed_first_and_active_second_attempt():
    planner = ScheduledPlanner(policy(), outcomes={(1, 1): 'no_query', (1, 3): RuntimeError('LP failed')})
    observed = []
    with pytest.raises(NumericalError) as caught:
        run(planner, history=HISTORY, cursor=ExecutionCursor(1, 1), recorder=observed.append)
    partial = caught.value.context
    assert planner.calls == [(1, 1), (1, 3)]
    assert len(partial.pending_cycle.attempts) == 1
    assert partial.pending_cycle.active_attempt_index == 2
    assert partial.pending_cycle.requested_depth == 3
    assert partial.planning_cycles == ()
    assert [type(event).__name__ for event in observed] == [
        'StateAnalyzed', 'PlanningAttemptStarted', 'PlanningAttemptCompleted', 'PlanningAttemptStarted']


def test_numerical_failure_at_short_depth_does_not_trigger_a_retry():
    planner = ScheduledPlanner(policy(), outcomes={(1, 1): RuntimeError('Qhull failed')})
    with pytest.raises(NumericalError):
        run(planner, history=HISTORY, cursor=ExecutionCursor(1, 1))
    assert planner.calls == [(1, 1)]


def test_continuation_binds_binary64_problem_policy_and_version():
    config = policy()
    checkpoint = SolveContinuation(PROBLEM, config, HISTORY, ExecutionCursor(1, 1))
    checkpoint.validate_for(PROBLEM, config)
    with pytest.raises(InputValidationError, match='different algorithm policy'):
        checkpoint.validate_for(PROBLEM, replace(config, min_expected_progress=None))
    signed = Problem(((1., -0.), (0., 1.), (.6, .6)))
    with pytest.raises(InputValidationError, match='different mathematical problem'):
        checkpoint.validate_for(signed, config)
    with pytest.raises(InputValidationError, match='unsupported'):
        replace(checkpoint, contract_version=1)
    with pytest.raises(InputValidationError):
        replace(checkpoint, execution_cursor=ExecutionCursor(0, 1))
    with pytest.raises(FrozenInstanceError):
        checkpoint.execution_cursor = ExecutionCursor(1, 2)


def test_public_api_rejects_mixed_history_and_continuation_before_session_creation(monkeypatch):
    import otqa
    import otqa.planning
    config = policy()
    checkpoint = SolveContinuation(PROBLEM, config, HISTORY, ExecutionCursor(1, 1))
    monkeypatch.setattr(otqa.planning, 'PlannerSession', lambda *args: pytest.fail('session created'))
    with pytest.raises(InputValidationError, match='mutually exclusive'):
        otqa.solve(PROBLEM, config, lambda query: '>', initial_answers=HISTORY, continuation=checkpoint)
    with pytest.raises(InputValidationError, match='SolveContinuation'):
        otqa.solve(PROBLEM, config, lambda query: '>', continuation=object())


def test_cursor_validation_and_cycle_resolution_do_not_accept_missing_or_duplicate_retry():
    config = policy()
    cursor = ExecutionCursor(1, 1)
    failed = selection(config, 1, outcome='no_query')
    with pytest.raises(PlanningInvariantError, match='exactly one full retry'):
        resolve_cycle(config, cursor, (failed,))
    with pytest.raises(InputValidationError):
        validate_cursor(policy(mode='receding'), cursor, 1)
    assert initial_cursor(config, 99) == ExecutionCursor(99, 3)


def test_progress_evidence_uses_strict_unrounded_subtraction_and_disabled_escape():
    threshold = .001
    equal = ProgressEvidence('candidate_count', threshold, 0., threshold, threshold, admissible=False)
    assert not equal.admissible
    disabled = ProgressEvidence('candidate_count', 2., 2., 0., None)
    assert disabled.admissible
    with pytest.raises(ValueError, match='strict threshold'):
        replace(equal, admissible=True)
