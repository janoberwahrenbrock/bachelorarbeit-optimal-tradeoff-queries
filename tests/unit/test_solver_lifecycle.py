"""Actual loop ordering and failure semantics with an analytical fake planner."""
from dataclasses import replace

import pytest

from otqa import AlgorithmPolicy, AnsweredQuery, Problem, Query, QueryBudget, SingleCandidateStop, VolumeConfidenceStop
from otqa.errors import AnswerProviderError, ExecutionContextError, InvalidAnswerError, ObserverError, PlanningInvariantError, RecorderError
from otqa.models import QueryCounts, StateAnalysis
from otqa.models.execution import PlanningAttempt, ProgressEvidence
from otqa.models.planning import FixedScore, NoQuery, PlanningDecision, QueryEvaluation
from otqa.solver import _drive


PROBLEM = Problem(((1.0, 0.0), (0.0, 1.0)))
QUERY = Query(0, 1, 1.0)
POLICY = AlgorithmPolicy('fixed', 2, 'both', 5, 'candidate_count', SingleCandidateStop())
BEFORE = StateAnalysis(0, (0, 1), ((0, 0.5), (1, 0.5)), ((0, 0.5), (1, 0.5)))
AFTER = StateAnalysis(1, (0,), ((0, 0.5),), ((0, 1.0),))
DECISION = PlanningDecision(QUERY, 2, FixedScore(1.0, 1.0, (1.0,)),
                            (('<', 0.5), ('=', 0.0), ('>', 0.5)), QueryEvaluation(QUERY, 1.0, ()))


class Planner:
    def __init__(self, analyses=(BEFORE, AFTER), *, decision=DECISION, close_error=None):
        self.analyses, self.decision, self.close_error = analyses, decision, close_error
        self.position = 0
        self.closed = False
        self.planned = 0

    def initial_state(self, answers):
        return tuple(answers)

    def analyze(self, state, *, volumes):
        assert volumes is True
        return self.analyses[self.position]

    def advance(self, state, answer):
        self.position += 1
        return state + (answer,)

    def plan(self, state, *, requested_depth):
        self.planned += 1
        if isinstance(self.decision, NoQuery):
            return PlanningAttempt(requested_depth, (requested_depth,), 'no_query')
        progress = ProgressEvidence('candidate_count', 2., 1., 1., .001)
        return PlanningAttempt(requested_depth, (requested_depth,), 'available', self.decision, progress)

    def close(self):
        self.closed = True
        if self.close_error is not None:
            raise self.close_error


def drive(planner, provider=lambda q: '>', *, policy=POLICY, history=(), budget=QueryBudget(), recorder=None, observer=None):
    return _drive(PROBLEM, policy, provider, budget=budget, history=history,
                  recorder=recorder, observer=observer, session=planner)


def test_callbacks_are_ordered_and_success_is_emitted_after_close():
    planner = Planner()
    events = []
    def record(event):
        events.append(('record', type(event).__name__))
        if type(event).__name__ == 'SolveFinished':
            assert planner.closed
    def observe(event):
        events.append(('observe', type(event).__name__))
    result = drive(planner, recorder=record, observer=observe)
    names = ['StateAnalyzed', 'PlanningAttemptStarted', 'PlanningAttemptCompleted', 'PlanningResolved',
             'QueryPlanned', 'QueryDispatched', 'AnswerReceived',
             'StateAnalyzed', 'QueryCompleted', 'SolveFinished']
    assert events == [(kind, name) for name in names for kind in ('record', 'observe')]
    assert result.query_counts == QueryCounts(0, 1, 1, 1)
    assert result.queries[0].after == AFTER
    assert result.selected_candidate_index == 0


def test_initial_history_budget_and_singleton_stop_precede_planning():
    planner = Planner((AFTER,))
    result = drive(planner, provider=lambda q: pytest.fail('provider called'),
                   history=(AnsweredQuery(QUERY, '>'),), budget=QueryBudget(1))
    assert result.solved and result.query_counts == QueryCounts(1, 0, 0, 1)
    assert planner.planned == 0


def test_budget_does_not_compute_an_extra_no_query():
    planner = Planner((replace(BEFORE, answered_total=1),))
    result = drive(planner, history=(AnsweredQuery(QUERY, '='),), budget=QueryBudget(1))
    assert result.termination_reason == 'max_questions'
    assert not result.solved and planner.planned == 0


def test_no_query_is_a_normal_unsolved_result():
    planner = Planner(decision=NoQuery(2))
    result = drive(planner)
    assert not result.solved and result.termination_reason == 'no_query'
    assert result.selected_candidate_index is None


def test_confidence_does_not_renormalize_and_uses_original_index_tie():
    state = StateAnalysis(0, (1, 0), ((1, 0.1), (0, 0.1)), ((1, 0.5), (0, 0.5)))
    policy = replace(POLICY, stopping=VolumeConfidenceStop(0.5))
    result = drive(Planner((state,)), policy=policy)
    assert result.selected_candidate_index == 0
    assert result.termination_reason == 'volume_confidence' and not result.exactly_solved


def test_recorder_dispatch_failure_stops_before_provider_and_preserves_dispatch():
    planner = Planner()
    def recorder(event):
        if type(event).__name__ == 'QueryDispatched':
            raise OSError('write failed')
    with pytest.raises(RecorderError) as caught:
        drive(planner, lambda q: pytest.fail('provider called'), recorder=recorder)
    assert planner.closed and isinstance(caught.value.__cause__, OSError)
    assert caught.value.context.query_counts == QueryCounts(0, 1, 0, 0)
    assert caught.value.context.open_query == QUERY


@pytest.mark.parametrize('provider, expected', [
    (lambda q: ' >', InvalidAnswerError),
    (lambda q: 1 / 0, AnswerProviderError),
])
def test_provider_error_does_not_accept_or_repeat_answer(provider, expected):
    planner = Planner()
    with pytest.raises(expected) as caught:
        drive(planner, provider)
    assert planner.closed and planner.planned == 1
    assert caught.value.context.query_counts == QueryCounts(0, 1, 0, 0)


def test_observer_failure_after_answer_preserves_accepted_memory_context():
    planner = Planner()
    def observer(event):
        if type(event).__name__ == 'AnswerReceived':
            raise RuntimeError('observer failed')
    with pytest.raises(ObserverError) as caught:
        drive(planner, observer=observer)
    assert caught.value.context.query_counts == QueryCounts(0, 1, 1, 1)
    assert len(caught.value.context.answers) == 1 and planner.closed


def test_cleanup_failure_never_emits_success():
    events = []
    with pytest.raises(ExecutionContextError):
        drive(Planner((replace(AFTER, answered_total=0),), close_error=RuntimeError('close failed')), recorder=events.append)
    assert all(type(event).__name__ != 'SolveFinished' for event in events)


def test_cleanup_keeps_original_provider_exception_primary():
    planner = Planner(close_error=RuntimeError('secondary close failure'))
    with pytest.raises(AnswerProviderError) as caught:
        drive(planner, lambda q: 1 / 0)
    assert isinstance(caught.value.__cause__, ZeroDivisionError)
    assert 'secondary close failure' in caught.value.__notes__[0]


def test_final_recorder_failure_is_not_a_normal_return():
    planner = Planner((replace(AFTER, answered_total=0),))
    def recorder(event):
        if type(event).__name__ == 'SolveFinished':
            raise OSError('terminal callback failed')
    with pytest.raises(RecorderError):
        drive(planner, recorder=recorder)
    assert planner.closed


def test_single_objective_error_publishes_empty_state_before_failure():
    planner = Planner((StateAnalysis(0, (), (), ()),))
    events = []
    with pytest.raises(PlanningInvariantError, match='feasible query state has no candidate alternatives'):
        drive(planner, recorder=events.append)
    assert [type(event).__name__ for event in events] == ['StateAnalyzed']
    assert planner.closed


def test_keyboard_interrupt_is_not_wrapped_as_a_provider_error():
    planner = Planner()
    def interrupt(query):
        raise KeyboardInterrupt()
    with pytest.raises(KeyboardInterrupt):
        drive(planner, interrupt)
    assert planner.closed
