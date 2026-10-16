"""Small explicit state trees exercise planning decisions without LP noise."""

from collections import OrderedDict
from dataclasses import dataclass
import sys
from types import ModuleType, SimpleNamespace

import pytest
import otqa.state  # noqa: F401 — bind the real package before replacing its narrow leaf seam.

from otqa.config import AlgorithmPolicy, SingleCandidateStop, SolverExecution, VolumeConfidenceStop
from otqa.models.core import Query
from otqa.models.planning import EfficiencyScore, QueryEvaluation
from otqa.planning.session import PlannerSession, _Evaluated


@dataclass(frozen=True)
class Node:
    name: str
    candidates: tuple
    history: tuple = ()
    shares: tuple = ()
    is_feasible: bool = True

    @property
    def analysis(self):
        return SimpleNamespace(candidates=self.candidates,
            candidate_volume_shares=dict(self.shares) if self.shares else None)

    @property
    def weight_space(self):
        return self.name


class Engine:
    def __init__(self, transitions):
        self.transitions = transitions

    def bind(self, state):
        return state

    def check(self, state):
        pass

    def ensure_analysis(self, state, **kwargs):
        return state

    def advance(self, state, answered, **kwargs):
        return self.transitions[state.name, answered.query.value, answered.answer]


def session(policy=None, transitions=None):
    instance = PlannerSession.__new__(PlannerSession)
    instance.policy = policy or AlgorithmPolicy("fixed", 2, "both", 5, "candidate_count", SingleCandidateStop())
    instance.execution = SolverExecution(1)
    instance._closed = False
    instance._worker = False
    instance._capture = instance._capture_options = None
    instance._session_id = "analytic-session"
    instance._plan_index = instance._task_counter = instance._observation_ordinal = 0
    instance._plan_address = None
    instance._plan_cache = OrderedDict()
    instance.states = Engine(transitions or {})
    instance.geometry = SimpleNamespace(probabilities=lambda space, query: {"<": 1.0, "=": 0.0, ">": 0.0})
    return instance


def queries(monkeypatch, mapping):
    module = ModuleType("otqa.queries")
    module.canonical_key = lambda query: (query.goal_index_a, query.goal_index_b, query.value)
    module.generate_queries = lambda state, depth: SimpleNamespace(
        query_candidates=mapping.get((state.name, depth), ()), query_sources={})
    monkeypatch.setitem(sys.modules, "otqa.queries", module)


def terminal_counts(monkeypatch, mapping, visited):
    module = ModuleType("otqa.state.analysis")

    def count(state, query, answer, probability, **kwargs):
        visited.append((state.name, query.value))
        return mapping[state.name, query.value], True

    module.compute_terminal_candidate_count = count
    monkeypatch.setitem(sys.modules, "otqa.state.analysis", module)


def test_fixed_only_refines_exactly_tied_best_queries(monkeypatch):
    a, b, c = (Query(0, 1, value) for value in (1, 2, 3))
    root = Node("root", tuple(range(4)))
    planner = session(transitions={
        ("root", 1.0, "<"): Node("a", (0, 1)),
        ("root", 2.0, "<"): Node("b", (0, 1)),
        ("root", 3.0, "<"): Node("c", (0, 1, 2)),
    })
    queries(monkeypatch, {("root", 2): (a, b, c)})
    visited = []
    terminal_counts(monkeypatch, {("root", 1.0): 3, ("root", 2.0): 2}, visited)
    result = planner.plan(root, requested_depth=planner.policy.depth).selected_plan
    assert result.query == b
    assert result.score.lexicographic_profile == (2.0, 2.0)
    assert [item.lexicographic_profile for item in result.horizons[0].evaluations] == [(2, 3), (2, 2), (3,)]
    assert visited == [("root", 1.0), ("root", 2.0)]


def test_fixed_query_identity_breaks_exact_full_tie(monkeypatch):
    first, second = Query(0, 1, 1), Query(0, 1, 2)
    root = Node("root", (0, 1, 2))
    planner = session(AlgorithmPolicy("fixed", 1, "both", 5, "candidate_count", SingleCandidateStop()))
    queries(monkeypatch, {("root", 1): (second, first)})
    terminal_counts(monkeypatch, {("root", 1.0): 2, ("root", 2.0): 2}, [])
    assert planner.plan(root, requested_depth=planner.policy.depth).selected_plan.query == first


def test_stop_aware_keeps_actual_candidates_separate_from_absorbed_loss(monkeypatch):
    query = Query(0, 1, 1)
    root = Node("root", (0, 1, 2, 3))
    child = Node("confident", (0, 1, 2), shares=((0, .99), (1, .005), (2, .005)))
    planner = session(AlgorithmPolicy("fixed", 2, "both", 5, "stop_aware", VolumeConfidenceStop(.99)),
                      {("root", 1.0, "<"): child})
    queries(monkeypatch, {("root", 2): (query,)})
    result = planner.plan(root, requested_depth=planner.policy.depth).selected_plan
    assert result.score.expected_terminal_candidates == 3
    assert result.score.expected_terminal_loss == 1
    assert result.score.expected_queries == 1
    assert result.score.lexicographic_profile == (3,)
    branch = result.evaluation.branches[0]
    assert branch.stop_reason == "volume_confidence"
    assert branch.expected_followup_queries == 0


def test_fixed_singleton_stop_aware_delegates_to_count_path(monkeypatch):
    query = Query(0, 1, 1)
    planner = session(AlgorithmPolicy("fixed", 1, "both", 5, "stop_aware", SingleCandidateStop()))
    queries(monkeypatch, {("root", 1): (query,)})
    terminal_counts(monkeypatch, {("root", 1.0): 2}, [])
    result = planner.plan(Node("root", (0, 1, 2)), requested_depth=planner.policy.depth).selected_plan
    assert result.score.expected_terminal_loss == 2
    assert result.score.expected_queries is None
    assert result.evaluation.expected_terminal_loss is None


def test_adaptive_depth_three_evaluates_all_horizons_and_uses_ratio_of_expectations(monkeypatch):
    q1, q2, q3 = (Query(0, 1, value) for value in (1, 2, 3))
    root = Node("root", tuple(range(5)))
    planner = session(AlgorithmPolicy("reduction_per_query", 3, "both", 5, "candidate_count", SingleCandidateStop()))
    queries(monkeypatch, {("root", 1): (q1,), ("root", 2): (q2,), ("root", 3): (q3,)})
    evaluated = []

    def evaluate(state, data, depth, mode, **kwargs):
        evaluated.append(depth)
        query, candidates, cost = {1: (q1, 3, 1), 2: (q2, 1, 2), 3: (q3, 1, 2.9)}[depth]
        return (_Evaluated(QueryEvaluation(query, candidates, ()), cost),)

    planner._evaluate_many = evaluate
    result = planner.plan(root, requested_depth=planner.policy.depth).selected_plan
    # H1 and H2 have rate two. Lower expected cost wins, not lower loss.
    assert evaluated == [1, 2, 3]
    assert result.horizon == 1
    assert result.query == q1
    assert isinstance(result.score, EfficiencyScore)
    assert result.score.rate == 2
    assert len(result.horizons) == 3


def test_h3_child_frontier_contains_only_complete_h2_options(monkeypatch):
    root = Node("child", (0, 1, 2))
    query = Query(0, 1, 2)
    planner = session(AlgorithmPolicy("reduction_per_query", 3, "both", 5, "candidate_count", SingleCandidateStop()))
    queries(monkeypatch, {("child", 2): (query,)})
    evaluation = QueryEvaluation(query, 2, ())
    seen = []

    def evaluate(state, data, depth, mode, **kwargs):
        seen.append((depth, mode, tuple(data.query_candidates)))
        return (_Evaluated(evaluation, 2),)

    planner._evaluate_many = evaluate
    frontier = planner._child_frontier(root)
    assert seen == [(2, "efficiency", (query,))]
    assert len(frontier) == 1
    assert frontier[0].expected_queries == 2
    assert frontier[0].evaluation.query == query
    assert not any(option.evaluation is None for option in frontier)


def test_no_query_horizons_remain_explicit(monkeypatch):
    planner = session(AlgorithmPolicy("reduction_per_query", 3, "both", 5, "candidate_count", SingleCandidateStop()))
    queries(monkeypatch, {})
    result = planner.plan(Node("root", (0, 1)), requested_depth=planner.policy.depth)
    assert result.outcome == "no_query"
    assert result.evaluated_horizons == (1, 2, 3)
    assert all(item.selected_plan is None and item.evaluated_query_count == 0 for item in result.horizon_evidence)


def test_session_close_rejects_new_plan_before_touching_state():
    planner = session()
    planner._closed = True
    with pytest.raises(RuntimeError, match="closed"):
        planner.plan(None, requested_depth=2)


def test_broken_pool_is_an_execution_failure_and_keeps_original_cause():
    from concurrent.futures.process import BrokenProcessPool
    from otqa.errors import ExecutionContextError

    cause = BrokenProcessPool("analytical process failure")

    def failed_result():
        raise cause

    with pytest.raises(ExecutionContextError) as caught:
        PlannerSession._receive(failed_result, None)
    assert caught.value.__cause__ is cause


def test_pool_submission_failure_is_an_execution_failure():
    from otqa.errors import ExecutionContextError
    cause = OSError("analytical dispatch failure")

    class FailedPool:
        def submit(self, *args):
            raise cause

    with pytest.raises(ExecutionContextError) as caught:
        PlannerSession._submit(FailedPool(), object())
    assert caught.value.__cause__ is cause


def test_pickling_failure_is_an_execution_failure_but_math_error_is_preserved():
    import pickle
    from otqa.errors import ExecutionContextError, NumericalError

    for cause in [pickle.PicklingError("analytical transfer failure"), NumericalError("analytical geometry failure")]:
        def failed_result():
            raise cause

        if isinstance(cause, pickle.PicklingError):
            with pytest.raises(ExecutionContextError) as caught:
                PlannerSession._receive(failed_result, None)
            assert caught.value.__cause__ is cause
        else:
            with pytest.raises(NumericalError) as caught:
                PlannerSession._receive(failed_result, None)
            assert caught.value is cause


@pytest.mark.parametrize("capture_enabled", [False, True])
def test_root_dispatch_refills_completed_slot_before_slow_first_query(monkeypatch, capture_enabled):
    """Root zero depends on root two starting, so ordered waiting would stall."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from otqa.planning.capture import EvaluationCaptureOptions, TaskCapture

    queries(monkeypatch, {})
    planner = session()
    planner.execution = SolverExecution(2)
    started_later = Event()
    delivered = []

    class Sink:
        def accept(self, block):
            if block.task_end:
                delivered.append(int(block.task_address[-1][-1]))

    if capture_enabled:
        planner._capture_options = EvaluationCaptureOptions(Sink(), 100_000, 100_000, 800_000, 800_000)
        planner._plan_address = ("analytical", 1)

    def evaluate(task):
        index = int(task.query.value)
        if index == 0:
            assert started_later.wait(2), "a free worker was blocked behind root zero"
        elif index == 2:
            started_later.set()
        result = _Evaluated(QueryEvaluation(task.query, float(3 - index), ()))
        if capture_enabled:
            capture = TaskCapture(*task.capture_address, *task.capture_limits)
            return result, capture.finish()
        return result

    with ThreadPoolExecutor(max_workers=2) as executor:
        class Pool:
            def submit(self, _function, task):
                if capture_enabled and task.query.value == 2:
                    assert 1 in delivered, "capture must be delivered before replacing its task"
                return executor.submit(evaluate, task)

        pool = Pool()
        planner._pool = lambda: pool
        candidates = tuple(Query(0, 1, value) for value in (0, 1, 2))
        values = planner._evaluate_many(Node("root", (0, 1, 2)),
            SimpleNamespace(query_candidates=candidates, query_sources={}), 3, "count", root=True)
    assert [value.evaluation.query for value in values] == list(candidates)
    assert [value.evaluation.expected_terminal_candidates for value in values] == [3, 2, 1]
    if capture_enabled:
        assert set(delivered) == {0, 1, 2}


def test_parallel_errors_keep_original_query_priority_and_cleanup_pool(monkeypatch):
    from concurrent.futures import Future

    queries(monkeypatch, {})
    planner = session()
    planner.execution = SolverExecution(2)
    earlier = RuntimeError("earlier mathematical failure")
    later = RuntimeError("later mathematical failure")
    submitted, shutdown = [], []

    class Pool:
        def submit(self, _function, task):
            submitted.append(task.query.value)
            future = Future()
            future.set_exception(earlier if task.query.value == 0 else later)
            return future

        def shutdown(self, **kwargs):
            shutdown.append(kwargs)

    pool = Pool()
    planner._executor = pool
    planner._pool = lambda: pool
    with pytest.raises(RuntimeError) as caught:
        planner._evaluate_many(Node("root", (0, 1, 2)), SimpleNamespace(
            query_candidates=tuple(Query(0, 1, value) for value in (0, 1, 2)), query_sources={}),
            3, "count", root=True)
    assert caught.value is earlier
    assert submitted == [0, 1]
    assert shutdown == [{"wait": True, "cancel_futures": True}]
    assert planner._executor is None


def test_parallel_sink_failure_stops_dispatch_and_cleans_pool(monkeypatch):
    from concurrent.futures import Future
    from otqa.planning.capture import EvaluationCaptureError, EvaluationCaptureOptions, TaskCapture

    queries(monkeypatch, {})
    planner = session()
    planner.execution = SolverExecution(2)
    cause = RuntimeError("analytical sink failure")
    submitted, shutdown = [], []

    class Sink:
        def accept(self, block):
            raise cause

    planner._capture_options = EvaluationCaptureOptions(Sink(), 100_000, 100_000, 800_000, 800_000)
    planner._plan_address = ("analytical", 1)

    class Pool:
        def submit(self, _function, task):
            submitted.append(task.query.value)
            capture = TaskCapture(*task.capture_address, *task.capture_limits)
            future = Future()
            future.set_result((_Evaluated(QueryEvaluation(task.query, 2, ())), capture.finish()))
            return future

        def shutdown(self, **kwargs):
            shutdown.append(kwargs)

    pool = Pool()
    planner._executor = pool
    planner._pool = lambda: pool
    with pytest.raises(EvaluationCaptureError) as caught:
        planner._evaluate_many(Node("root", (0, 1, 2)), SimpleNamespace(
            query_candidates=tuple(Query(0, 1, value) for value in (0, 1, 2)), query_sources={}),
            3, "count", root=True)
    assert caught.value.__cause__ is cause
    assert submitted == [0, 1]
    assert shutdown == [{"wait": True, "cancel_futures": True}]
    assert planner._executor is None


def test_later_completed_error_waits_for_earlier_query_error(monkeypatch):
    from concurrent.futures import Future
    import otqa.planning.session as module

    queries(monkeypatch, {})
    planner = session()
    planner.execution = SolverExecution(2)
    earlier, later = RuntimeError("root zero"), RuntimeError("root one")
    futures, submitted = [], []

    class Pool:
        def submit(self, _function, task):
            submitted.append(task.query.value)
            future = Future()
            if task.query.value == 1:
                future.set_exception(later)
            futures.append(future)
            return future

        def shutdown(self, **kwargs):
            pass

    waits = []
    original_wait = module.wait

    def controlled_wait(pending, **kwargs):
        waits.append(tuple(pending))
        if len(waits) == 1:
            # The second task arrives first. Its observation cannot determine
            # the mathematical error while the earlier task is unresolved.
            futures[0].set_exception(earlier)
            return {futures[1]}, {futures[0]}
        return original_wait(pending, **kwargs)

    monkeypatch.setattr(module, "wait", controlled_wait)
    pool = Pool()
    planner._executor = pool
    planner._pool = lambda: pool
    with pytest.raises(RuntimeError) as caught:
        planner._evaluate_many(Node("root", (0, 1, 2)), SimpleNamespace(
            query_candidates=tuple(Query(0, 1, value) for value in (0, 1, 2)), query_sources={}),
            3, "count", root=True)
    assert caught.value is earlier
    assert submitted == [0, 1]
    assert len(waits) == 2


def worker_context(monkeypatch):
    import otqa.planning.session as module
    monkeypatch.setattr(module, "_WORKER", None)
    monkeypatch.setattr(module, "_WORKER_CONTEXT", None)
    monkeypatch.setattr(module, "_WORKER_FAILURE", None)
    return module


def test_worker_initializer_registers_inputs_without_creating_session(monkeypatch):
    module = worker_context(monkeypatch)
    calls = []

    def forbidden(*args, **kwargs):
        calls.append(args)
        raise AssertionError("idle worker constructed a numerical session")

    monkeypatch.setattr(module, "PlannerSession", forbidden)
    config = AlgorithmPolicy("fixed", 1, "both", 5, "candidate_count", SingleCandidateStop())
    execution = SolverExecution(8)
    module._initialize_worker("problem", config, execution, None, forbidden, "owner")
    assert calls == []
    assert module._WORKER_CONTEXT == ("problem", config, execution, None, forbidden, "owner")
    assert module._WORKER is None


def test_worker_creates_session_and_finalizer_only_once_on_first_task(monkeypatch):
    import multiprocessing.util
    module = worker_context(monkeypatch)
    created, finalized, closed, executed = [], [], [], []

    class Worker:
        def __init__(self, *args, **kwargs):
            created.append((args, kwargs))

        def close(self):
            closed.append(self)

        def _execute_task(self, task):
            executed.append(task)
            return task, ()

    monkeypatch.setattr(module, "PlannerSession", Worker)
    monkeypatch.setattr(multiprocessing.util, "Finalize", lambda owner, callback, **kw: finalized.append((owner, callback, kw)))
    module._initialize_worker("problem", "policy", SolverExecution(8), None, None, "owner")
    assert not created and not finalized
    first, second = object(), object()
    assert module._run_worker(first) is first
    assert module._run_worker(second) is second
    assert len(created) == len(finalized) == 1
    assert created[0][0][2].workers == 1
    assert created[0][1] == {"backend_factory": None, "_session_id": "owner", "_worker": True}
    assert executed == [first, second]
    assert finalized[0][0] is module._WORKER
    assert finalized[0][2] == {"exitpriority": 10}
    assert not closed
    finalized[0][1]()
    assert closed == [module._WORKER]
    with pytest.raises(module.ExecutionContextError, match="already registered"):
        module._initialize_worker("foreign", "foreign", SolverExecution(), None, None, "foreign")
    assert closed == [module._WORKER]


def test_failed_first_worker_factory_is_typed_and_not_retried(monkeypatch):
    module = worker_context(monkeypatch)
    calls = []
    cause = ValueError("analytical first-use setup failure")

    def factory(*args, **kwargs):
        calls.append(args)
        raise cause

    monkeypatch.setattr(module, "PlannerSession", factory)
    module._initialize_worker("problem", "policy", SolverExecution(8), None, None, "owner")
    with pytest.raises(module.ExecutionContextError) as first:
        module._run_worker(object())
    assert first.value.__cause__ is cause
    with pytest.raises(module.ExecutionContextError) as second:
        module._run_worker(object())
    assert second.value is first.value
    assert len(calls) == 1
    assert module._WORKER is None


def test_worker_finalize_setup_failure_closes_only_its_new_session(monkeypatch):
    import multiprocessing.util
    module = worker_context(monkeypatch)
    created, closed = [], []
    cause = RuntimeError("analytical finalizer registration failure")

    class Worker:
        def __init__(self, *args, **kwargs):
            created.append(self)

        def close(self):
            closed.append(self)

    def fail(*args, **kwargs):
        raise cause

    monkeypatch.setattr(module, "PlannerSession", Worker)
    monkeypatch.setattr(multiprocessing.util, "Finalize", fail)
    module._initialize_worker("problem", "policy", SolverExecution(8), None, None, "owner")
    with pytest.raises(module.ExecutionContextError) as caught:
        module._run_worker(object())
    assert caught.value.__cause__ is cause
    assert closed == created
    assert len(closed) == 1
    assert module._WORKER is None


def test_lazy_worker_preserves_mathematical_failure_after_setup(monkeypatch):
    import multiprocessing.util
    module = worker_context(monkeypatch)
    cause = RuntimeError("analytical mathematical evaluation failure")

    class Worker:
        def __init__(self, *args, **kwargs):
            pass

        def close(self):
            pass

        def _execute_task(self, task):
            raise cause

    monkeypatch.setattr(module, "PlannerSession", Worker)
    monkeypatch.setattr(multiprocessing.util, "Finalize", lambda *a, **kw: None)
    module._initialize_worker("problem", "policy", SolverExecution(8), None, None, "owner")
    with pytest.raises(RuntimeError) as caught:
        module._run_worker(object())
    assert caught.value is cause
    assert module._WORKER_FAILURE is None
    assert module._WORKER is not None
