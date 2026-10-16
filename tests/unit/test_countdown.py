"""Countdown execution reuses ordinary fixed planning at the remaining depth.

All examples are constructed analytically here. The reference trajectory uses
an ordinary fixed planner with an explicitly selected depth at each answer; it
does not implement or call the countdown scheduling method.
"""

from dataclasses import replace
import multiprocessing

import pytest

from otqa import (
    AlgorithmPolicy, AnsweredQuery, Problem, Query, QueryBudget,
    SingleCandidateStop, SolverExecution, VolumeConfidenceStop, solve,
    ExecutionCursor, SolveContinuation,
)
from otqa.answers import SimulatedAnswers
from otqa.errors import InputValidationError
from otqa.models import QueryPlanned
from otqa.models.execution import PlanningAttempt, ProgressEvidence
from otqa.models.planning import FixedScore, PlanningDecision, QueryEvaluation
from otqa.execution import cursor_after_answer, initial_cursor
from otqa.planning import PlannerSession
from otqa.planning.capture import EvaluationCaptureOptions


PROBLEM = Problem(((1., 0.), (0., 1.), (.6, .6)))
WEIGHTS = (.55, .45)
NEUTRAL_ANSWER = AnsweredQuery(Query(0, 1, 0.), '>')


def policy(depth=2, *, execution='countdown', planning='candidate_count', stopping=None):
    return AlgorithmPolicy('fixed', depth, 'both', 3, planning,
                           stopping or SingleCandidateStop(), horizon_execution=execution)


def test_existing_policy_constructor_keeps_receding_horizon_default():
    ordinary = AlgorithmPolicy('fixed', 2, 'both', 3, 'candidate_count', SingleCandidateStop())
    explicit = policy(execution='receding')
    assert ordinary == explicit
    assert ordinary.horizon_execution == 'receding'
    assert ordinary.min_expected_progress == .001
    adaptive = replace(ordinary, query_strategy='reduction_per_query')
    assert initial_cursor(adaptive, 3) == ExecutionCursor(3, 2)


@pytest.mark.parametrize('depth,expected', [
    (1, [1, 1, 1, 1, 1, 1, 1]),
    (2, [2, 1, 2, 1, 2, 1, 2]),
    (3, [3, 2, 1, 3, 2, 1, 3]),
])
def test_explicit_depth_schedule_advances_only_after_actual_answers(depth, expected):
    config = policy(depth)
    cursor = initial_cursor(config, 0)
    actual = []
    for _ in expected:
        actual.append(cursor.remaining_depth)
        decision = PlanningDecision(Query(0, 1, 1.), cursor.remaining_depth,
                                    FixedScore(1., 1., (1.,)), (), QueryEvaluation(Query(0, 1, 1.), 1., ()))
        cursor = cursor_after_answer(config, cursor, decision)
    assert actual == expected


@pytest.mark.parametrize('execution', [None, True, 1, '', 'block', 'COUNTDOWN'])
def test_unknown_horizon_execution_is_rejected(execution):
    with pytest.raises(InputValidationError):
        policy(execution=execution)


def test_countdown_is_explicitly_rejected_for_adaptive_strategy():
    with pytest.raises(InputValidationError):
        replace(policy(), query_strategy='reduction_per_query')


@pytest.mark.parametrize('count', [True, -1, 1.0, '1', None])
def test_depth_phase_requires_a_nonnegative_integer_answer_count(count):
    with pytest.raises(InputValidationError):
        initial_cursor(policy(), count)


@pytest.mark.parametrize('depth,planning,expected_horizons', [
    (2, 'candidate_count', (2, 1, 2)),
    (3, 'candidate_count', (3, 2, 1)),
    (2, 'stop_aware', (2, 1)),
    (3, 'stop_aware', (3, 2, 1)),
])
def test_complete_countdown_matches_independent_remaining_depth_reference(depth, expected_horizons, planning):
    config = policy(depth, planning=planning,
                    stopping=VolumeConfidenceStop(.99) if planning == 'stop_aware' else SingleCandidateStop())
    expected = []
    history = []
    provider = SimulatedAnswers(WEIGHTS)
    # The explicit literal sequence supplies the reference depths. It also
    # exercises a complete block rollover for the depth-two trajectory.
    for remaining in expected_horizons:
        ordinary = replace(config, depth=remaining, horizon_execution='receding')
        with PlannerSession(PROBLEM, ordinary, SolverExecution()) as planner:
            state = planner.initial_state(tuple(history))
            decision = planner.plan(state, requested_depth=remaining).selected_plan
        assert isinstance(decision, PlanningDecision)
        expected.append(decision)
        history.append(AnsweredQuery(decision.query, provider(decision.query)))

    result = solve(PROBLEM, config, provider, budget=QueryBudget(8))
    assert result.solved and result.selected_candidate_index == 2
    if planning == 'candidate_count':
        assert result.exactly_solved and result.termination_reason == 'exact_single_candidate'
        assert result.final_state.candidate_count == 1
    elif result.exactly_solved:
        assert result.termination_reason == 'exact_single_candidate'
        assert result.final_state.candidate_count == 1
    else:
        assert result.termination_reason == 'volume_confidence'
        assert result.final_state.candidate_count > 1
        assert result.selected_candidate_volume_share >= .99
    assert result.answers == tuple(history)
    assert tuple(record.planning.horizon for record in result.queries) == expected_horizons
    assert len(result.queries) == len(expected)
    for record, reference in zip(result.queries, expected, strict=True):
        actual = record.planning
        assert actual.query == reference.query
        assert actual.query.value.hex() == reference.query.value.hex()
        assert actual.horizon == reference.horizon
        assert actual.score.expected_terminal_candidates == pytest.approx(
            reference.score.expected_terminal_candidates, abs=1e-12, rel=1e-12)
        assert actual.score.expected_terminal_loss == pytest.approx(
            reference.score.expected_terminal_loss, abs=1e-12, rel=1e-12)
        assert actual.score.lexicographic_profile == pytest.approx(
            reference.score.lexicographic_profile, abs=1e-12, rel=1e-12)
        assert tuple(answer for answer, _ in actual.answer_probabilities) == tuple(
            answer for answer, _ in reference.answer_probabilities)
        assert tuple(value for _, value in actual.answer_probabilities) == pytest.approx(
            tuple(value for _, value in reference.answer_probabilities), abs=1e-12, rel=1e-12)
        assert actual.evaluation.query_source == reference.evaluation.query_source
        if actual.horizon == 1:
            assert actual.evaluation.query_source == 'ratio'


@pytest.mark.parametrize('depth', [2, 3])
@pytest.mark.parametrize('prefix_length', [1, 2])
def test_explicit_continuation_preserves_block_phase_and_complete_trajectory(depth, prefix_length):
    config = policy(depth)
    complete = solve(PROBLEM, config, SimulatedAnswers(WEIGHTS), budget=QueryBudget(8))
    prefix = complete.answers[:prefix_length]
    cursor = complete.planning_cycles[prefix_length - 1].proposed_cursor_after_answer
    continuation = SolveContinuation(PROBLEM, config, prefix, cursor)
    resumed = solve(PROBLEM, config, SimulatedAnswers(WEIGHTS),
                    continuation=continuation, budget=QueryBudget(8))
    assert resumed.answers == complete.answers
    assert resumed.selected_candidate_index == complete.selected_candidate_index
    assert resumed.query_counts.initial_answers == prefix_length
    assert resumed.query_counts.answered_new == len(complete.answers) - prefix_length
    assert tuple(record.planning.horizon for record in resumed.queries) == tuple(
        record.planning.horizon for record in complete.queries[prefix_length:])
    assert resumed.queries[0].planning.horizon == cursor.remaining_depth


def test_depth_one_countdown_preserves_default_full_numerical_decisions():
    ordinary = solve(PROBLEM, policy(1, execution='receding'), SimulatedAnswers(WEIGHTS),
                     budget=QueryBudget(8))
    countdown = solve(PROBLEM, policy(1), SimulatedAnswers(WEIGHTS), budget=QueryBudget(8))
    assert countdown.answers == ordinary.answers
    assert countdown.queries == ordinary.queries
    assert countdown.selected_candidate_index == ordinary.selected_candidate_index


def test_cache_keeps_history_and_reports_remaining_depth_without_consuming_a_turn(monkeypatch):
    root_depths = []
    with PlannerSession(PROBLEM, policy(), SolverExecution()) as planner:
        original = planner._fixed

        def observe(state, depth, *, root=False):
            if root:
                root_depths.append(depth)
            return original(state, depth, root=root)

        monkeypatch.setattr(planner, '_fixed', observe)
        root = planner.initial_state()
        first = planner.plan(root, requested_depth=2)
        assert planner.plan(root, requested_depth=2) is first
        odd = planner.initial_state((NEUTRAL_ANSWER,))
        second = planner.plan(odd, requested_depth=1)
        assert second.selected_plan.horizon == 1
        assert planner.plan(odd, requested_depth=1) is second
        even = planner.initial_state((NEUTRAL_ANSWER, NEUTRAL_ANSWER))
        third = planner.plan(even, requested_depth=2)
        assert third.selected_plan.horizon == 2
        assert third is not first
        assert planner.plan(even, requested_depth=2) is third
        assert len(planner._plan_cache) == 3
    assert root_depths == [2, 1, 2]


@pytest.mark.parametrize('reason', ['singleton', 'confidence', 'budget'])
def test_stopping_and_total_answer_budget_precede_followup_planning(monkeypatch, reason):
    problem = Problem(((1., 0.), (0., 1.)))
    history = (AnsweredQuery(Query(0, 1, .91 if reason == 'confidence' else 1.001), '>'),)
    config = policy(stopping=VolumeConfidenceStop(.95) if reason == 'confidence' else SingleCandidateStop())
    if reason == 'budget':
        # This history preserves both candidates; the accepted initial answer
        # consumes the whole budget even though the block has a question left.
        history = (NEUTRAL_ANSWER,)

    def fail_plan(*args):
        pytest.fail('a terminal state or exhausted budget must precede countdown planning')

    monkeypatch.setattr(PlannerSession, 'plan', fail_plan)
    result = solve(problem, config,
                   lambda query: pytest.fail('provider must not be called'),
                   initial_answers=history, budget=QueryBudget(1) if reason == 'budget' else QueryBudget())
    assert result.query_counts.answered_total == 1
    assert result.query_counts.dispatched_new == result.query_counts.answered_new == 0
    assert result.termination_reason == {
        'singleton': 'exact_single_candidate', 'confidence': 'volume_confidence', 'budget': 'max_questions',
    }[reason]


def test_no_query_at_remaining_depth_one_checks_full_depth_before_progress_stop():
    duplicates = Problem(((1., 0.), (1., 0.)))
    history = (NEUTRAL_ANSWER,)
    # Duplicates leave no Ratio query at one and only zero-gain grid queries
    # at two. Both distinct attempt outcomes must remain visible.
    with PlannerSession(duplicates, policy(execution='receding'), SolverExecution()) as planner:
        assert planner.plan(planner.initial_state(history), requested_depth=2).outcome == 'insufficient_expected_progress'
    with PlannerSession(duplicates, policy(), SolverExecution()) as planner:
        assert planner.plan(planner.initial_state(history), requested_depth=1).outcome == 'no_query'
    config = policy()
    result = solve(duplicates, policy(),
                   lambda query: pytest.fail('zero-gain replacement must not be dispatched'),
                   continuation=SolveContinuation(duplicates, config, history, ExecutionCursor(1, 1)),
                   budget=QueryBudget(2))
    assert not result.solved and result.termination_reason == 'insufficient_expected_progress'
    assert [item.requested_depth for item in result.planning_cycles[0].attempts] == [1, 2]
    assert result.query_counts.answered_total == 1
    assert result.query_counts.dispatched_new == 0


@pytest.mark.parametrize('value,reason,remaining_candidates', [
    (.91, 'volume_confidence', 2),
    (1.001, 'exact_single_candidate', 1),
])
def test_terminal_state_after_actual_first_answer_skips_the_remaining_query(
        monkeypatch, value, reason, remaining_candidates):
    problem = Problem(((1., 0.), (0., 1.)))
    # Exercise the solver's stop boundary with a declared first query. A free
    # numerical planner may instead choose an exact separating query, which
    # legitimately invokes singleton precedence rather than confidence.
    query = Query(0, 1, value)

    def first_plan(self, state, *, requested_depth):
        assert requested_depth == 2 and not state.history
        decision = PlanningDecision(query, 2, FixedScore(1., 1., (1.,)), (),
                                    QueryEvaluation(query, 1., ()))
        progress = ProgressEvidence('candidate_count', 2., 1., 1., .001)
        return PlanningAttempt(2, (2,), 'available', decision, progress)

    monkeypatch.setattr(PlannerSession, 'plan', first_plan)
    events = []
    result = solve(problem, policy(stopping=VolumeConfidenceStop(.95)),
                   SimulatedAnswers((.9, .1)), recorder=events.append, budget=QueryBudget(8))
    assert result.solved and result.termination_reason == reason
    assert result.exactly_solved == (reason == 'exact_single_candidate')
    assert result.selected_candidate_index == 0
    assert result.final_state.candidate_count == remaining_candidates
    if reason == 'volume_confidence':
        assert .95 <= result.selected_candidate_volume_share < 1.
    assert result.query_counts.answered_new == 1
    decisions = [event.planning for event in events if isinstance(event, QueryPlanned)]
    assert tuple(decision.horizon for decision in decisions) == (2,)


def test_countdown_serial_and_owned_process_pool_preserve_full_trajectory():
    serial = solve(PROBLEM, policy(), SimulatedAnswers(WEIGHTS), budget=QueryBudget(8))
    parallel = solve(PROBLEM, policy(), SimulatedAnswers(WEIGHTS), budget=QueryBudget(8),
                     execution=SolverExecution(2, multiprocessing.get_context('spawn')))
    assert parallel == serial


@pytest.mark.parametrize('depth,remaining', [(2, 1), (3, 2)])
def test_capture_records_remaining_horizon_and_preserves_cached_countdown_decision(depth, remaining):
    class Sink:
        def __init__(self):
            self.blocks = []

        def accept(self, block):
            self.blocks.append(block)

    config = policy(depth)
    history = (NEUTRAL_ANSWER,)
    with PlannerSession(PROBLEM, config, SolverExecution()) as ordinary:
        expected = ordinary.plan(ordinary.initial_state(history), requested_depth=remaining)
    sink = Sink()
    capture = EvaluationCaptureOptions(sink, 1_000_000, 10_000_000, 40_000_000, 40_000_000)
    with PlannerSession(PROBLEM, config, SolverExecution(), evaluation_capture=capture) as planner:
        state = planner.initial_state(history)
        actual = planner.plan(state, requested_depth=remaining)
        first_blocks = tuple(sink.blocks)
        assert actual == expected
        assert actual.selected_plan.horizon == remaining
        assert planner.plan(state, requested_depth=remaining) is actual
        repeated_blocks = sink.blocks[len(first_blocks):]
        repeated = [item for block in repeated_blocks for item in block.observations]
        reuse = [item for item in repeated if item.kind == 'cache']
        assert len(reuse) == 1
        assert reuse[0].value.value == ('reused_plan', (planner._session_id, 1))
        assert not any(item.kind in ('candidate_inventory', 'root_evaluation') for item in repeated)

    first = [item for block in first_blocks for item in block.observations]
    for observations in (first, repeated):
        begin = [item for item in observations if item.kind == 'plan_boundary'
                 and item.mathematical_address[-1] == 'begin']
        assert len(begin) == 1
        assert begin[0].value.value[1:] == ('fixed', remaining)
        assert any(item.kind == 'plan_boundary' and item.mathematical_address[-1] == 'end'
                   for item in observations)
    # Restrict source observations to this actual root. Descendant inventories
    # in a depth-two search legitimately use their own Ratio-only final level.
    root_sources = {
        item.value.value[1] for item in first
        if item.kind == 'candidate_inventory'
        and len(item.mathematical_address[1]) == len(history)
        and item.mathematical_address[2] == remaining
        and isinstance(item.value.value, tuple)
        and len(item.value.value) == 4
        and item.value.value[0] == 'filter'
        and item.value.value[1].startswith('source_')
    }
    assert root_sources == ({'source_ratio'} if remaining == 1 else {'source_ratio', 'source_grid'})
