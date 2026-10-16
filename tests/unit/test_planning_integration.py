"""New analytical fixtures exercise native geometry and process ownership."""

import multiprocessing
import os
import pickle

import pytest

from otqa import AlgorithmPolicy, Problem, SingleCandidateStop, SolverExecution, VolumeConfidenceStop
from otqa.models.core import AnsweredQuery, Query
from otqa.planning import PlannerSession
from otqa.planning.capture import EvaluationCaptureError, EvaluationCaptureOptions


MATRIX = ((1.0, 0.0), (0.0, 1.0), (.6, .6))


class Sink:
    def __init__(self):
        self.blocks = []
        self.parent_pid = os.getpid()

    def accept(self, block):
        assert os.getpid() == self.parent_pid
        self.blocks.append(block)


def policy(strategy="fixed", depth=2, *, stop_aware=False):
    return AlgorithmPolicy(strategy, depth, "both", 5,
        "stop_aware" if stop_aware else "candidate_count",
        VolumeConfidenceStop(.99) if stop_aware else SingleCandidateStop())


@pytest.mark.parametrize("strategy", ["fixed", "reduction_per_query"])
@pytest.mark.parametrize("stop_aware", [False, True])
def test_capture_on_off_preserves_full_decision(strategy, stop_aware):
    config = policy(strategy, stop_aware=stop_aware)
    with PlannerSession(Problem(MATRIX), config, SolverExecution()) as ordinary:
        expected = ordinary.plan(ordinary.initial_state(), requested_depth=ordinary.policy.depth)
    sink = Sink()
    capture = EvaluationCaptureOptions(sink, 1_000_000, 10_000_000, 40_000_000, 40_000_000)
    with PlannerSession(Problem(MATRIX), config, SolverExecution(), evaluation_capture=capture) as diagnostic:
        actual = diagnostic.plan(diagnostic.initial_state(), requested_depth=diagnostic.policy.depth)
    assert actual == expected
    assert sink.blocks
    tasks = {}
    for block in sink.blocks:
        tasks.setdefault(block.task_address, []).append(block)
    for blocks in tasks.values():
        assert [item.block_ordinal for item in blocks] == list(range(len(blocks)))
        assert blocks[-1].task_end
        assert all(not item.task_end for item in blocks[:-1])
    kinds = {item.kind for block in sink.blocks for item in block.observations}
    assert {"plan_boundary", "candidate_inventory", "root_evaluation"} <= kinds


def test_capture_h3_contains_full_child_options_frontiers_and_combination():
    sink = Sink()
    capture = EvaluationCaptureOptions(sink, 2_000_000, 40_000_000, 160_000_000, 160_000_000)
    with PlannerSession(Problem(MATRIX), policy("reduction_per_query", 3), SolverExecution(),
                        evaluation_capture=capture) as planner:
        result = planner.plan(planner.initial_state(), requested_depth=planner.policy.depth)
    assert result.evaluated_horizons == (1, 2, 3)
    kinds = {item.kind for block in sink.blocks for item in block.observations}
    assert {"child_options", "frontier_projection", "combination_choice"} <= kinds
    decisions = [item for block in sink.blocks for item in block.observations
                 if item.kind == "frontier_projection" and item.value.value[0] == "pruning_decision"]
    assert {item.value.value[1] for item in decisions} == {"child_options", "weighted_combinations"}
    assert {item.value.value[5] for item in decisions} == {
        "certified_nondominated", "certified_dominance",
    }
    assert all(item.mathematical_address[2] in (2, 3) for item in decisions)


@pytest.mark.parametrize("capture_enabled", [False, True])
def test_own_process_pool_reuses_workers_and_preserves_decision(capture_enabled):
    config = policy("reduction_per_query", 2)
    with PlannerSession(Problem(MATRIX), config, SolverExecution()) as ordinary:
        expected = ordinary.plan(ordinary.initial_state(), requested_depth=ordinary.policy.depth)
    sink = Sink()
    capture = EvaluationCaptureOptions(sink, 1_000_000, 10_000_000, 80_000_000, 80_000_000)
    execution = SolverExecution(2, multiprocessing.get_context("spawn"))
    with PlannerSession(Problem(MATRIX), config, execution,
                        evaluation_capture=capture if capture_enabled else None) as parallel:
        state = parallel.initial_state()
        actual = parallel.plan(state, requested_depth=parallel.policy.depth)
        pool = parallel._executor
        assert pool is not None
        assert actual == expected
        child = parallel.advance(state, AnsweredQuery(actual.selected_plan.query, "<"))
        parallel.plan(child, requested_depth=parallel.policy.depth)
        assert parallel._executor is pool
    assert parallel._closed
    assert all(block.task_address[0] in ("parent", "parent_observation", "root") for block in sink.blocks)
    assert bool(sink.blocks) is capture_enabled


def test_prepared_state_pickles_no_native_backend_or_geometry_owner():
    with PlannerSession(Problem(MATRIX), policy(), SolverExecution()) as planner:
        state = planner.initial_state()
        data = pickle.dumps(state)
        clone = pickle.loads(data)
        assert not hasattr(clone.weight_space, "_geometry_owner")
        # A verified same-session bind restores the worker-local handles.
        bound = planner.states.bind(clone)
        assert bound.analysis == state.analysis
        assert bound.history == state.history
    assert b"GeometrySession" not in data
    assert b"LinearProgramBackend" not in data


def test_foreign_session_state_is_rejected():
    with PlannerSession(Problem(MATRIX), policy(), SolverExecution()) as a, PlannerSession(
        Problem(MATRIX), policy(), SolverExecution()) as b:
        with pytest.raises(ValueError, match="another solver session"):
            b.plan(a.initial_state(), requested_depth=b.policy.depth)


def test_planning_cache_preserves_signed_zero_in_initial_history_identity():
    with PlannerSession(Problem(MATRIX), policy(depth=1), SolverExecution()) as planner:
        positive = planner.initial_state((AnsweredQuery(Query(0, 1, 0.0), ">"),))
        negative = planner.initial_state((AnsweredQuery(Query(0, 1, -0.0), ">"),))
        assert positive.history[0].query.value.hex() == "0x0.0p+0"
        assert negative.history[0].query.value.hex() == "-0x0.0p+0"
        a, b = planner.plan(positive, requested_depth=planner.policy.depth), planner.plan(negative, requested_depth=planner.policy.depth)
        assert a == b
        assert a is not b
        assert len(planner._plan_cache) == 2


def test_capture_budget_failure_closes_session_via_context_manager():
    sink = Sink()
    options = EvaluationCaptureOptions(sink, 256, 1024, 4096, 4096)
    planner = PlannerSession(Problem(MATRIX), policy(), SolverExecution(), evaluation_capture=options)
    with pytest.raises(EvaluationCaptureError):
        with planner:
            planner.plan(planner.initial_state(), requested_depth=planner.policy.depth)
    assert planner._closed


def test_capture_rejects_dispatch_that_would_exceed_pending_budget():
    options = EvaluationCaptureOptions(Sink(), 1000, 10_000, 10_000, 10_000)
    with pytest.raises(ValueError, match="outstanding root tasks"):
        PlannerSession(Problem(MATRIX), policy(), SolverExecution(2), evaluation_capture=options)


def test_capture_failure_retains_mathematical_error_and_completed_observations():
    sink = Sink()
    options = EvaluationCaptureOptions(sink, 1_000_000, 10_000_000, 40_000_000, 40_000_000)
    cause = RuntimeError("analytical backend failure")
    with PlannerSession(Problem(MATRIX), policy(), SolverExecution(), evaluation_capture=options) as planner:
        state = planner.initial_state()

        def fail(*args, **kwargs):
            raise cause

        planner.geometry.probabilities = fail
        with pytest.raises(RuntimeError, match="analytical backend failure") as caught:
            planner.plan(state, requested_depth=planner.policy.depth)
        assert caught.value is cause
        assert cause.evaluation_capture_complete is False
        assert cause.evaluation_capture_blocks
    observations = [item for block in sink.blocks for item in block.observations]
    assert any(item.kind == "error" for item in observations)
    assert not any(item.kind == "plan_boundary" and item.mathematical_address[-1] == "end" for item in observations)


def test_capture_cache_reuse_links_the_original_plan_and_completes_new_plan():
    sink = Sink()
    options = EvaluationCaptureOptions(sink, 1_000_000, 10_000_000, 40_000_000, 40_000_000)
    with PlannerSession(Problem(MATRIX), policy(depth=1), SolverExecution(), evaluation_capture=options) as planner:
        state = planner.initial_state()
        first = planner.plan(state, requested_depth=planner.policy.depth)
        count = len(sink.blocks)
        second = planner.plan(state, requested_depth=planner.policy.depth)
        assert second is first
        later = sink.blocks[count:]
        observations = [item for block in later for item in block.observations]
        cached = next(item for item in observations if item.kind == "cache")
        assert cached.value.value == ("reused_plan", (planner._session_id, 1))
        assert any(item.kind == "plan_boundary" and item.mathematical_address[-1] == "end" for item in observations)
        assert not any(item.kind == "root_evaluation" for item in observations)


def test_disabled_capture_never_instantiates_diagnostic_collectors(monkeypatch):
    import otqa.planning.session as module

    def fail(*args, **kwargs):
        raise AssertionError("diagnostic collector allocated in ordinary planning")

    monkeypatch.setattr(module, "TaskCapture", fail)
    with PlannerSession(Problem(MATRIX), policy(depth=1), SolverExecution()) as planner:
        planner.plan(planner.initial_state(), requested_depth=planner.policy.depth)
        assert planner._captured_plans is None
        assert planner._plan_address is None


def test_pool_startup_failure_has_typed_cause_and_cleans_parent(monkeypatch):
    import otqa.planning.session as module
    from otqa.errors import ExecutionContextError
    cause = OSError("analytical pool startup failure")

    def fail(*args, **kwargs):
        raise cause

    monkeypatch.setattr(module, "ProcessPoolExecutor", fail)
    planner = PlannerSession(Problem(MATRIX), policy(), SolverExecution(2))
    with pytest.raises(ExecutionContextError) as caught:
        with planner:
            planner.plan(planner.initial_state(), requested_depth=planner.policy.depth)
    assert caught.value.__cause__ is cause
    assert planner._closed
    assert planner.geometry.closed
    assert planner._executor is None


def _fail_worker_initialization():
    if multiprocessing.parent_process() is not None:
        raise RuntimeError("analytical worker initializer failure")
    from otqa.numerics.lp import LinearProgramBackend
    return LinearProgramBackend()


def test_real_worker_initializer_failure_does_not_leave_owned_processes():
    from otqa.errors import ExecutionContextError
    existing = {child.pid for child in multiprocessing.active_children()}
    planner = PlannerSession(Problem(MATRIX), policy(),
        SolverExecution(2, multiprocessing.get_context("spawn")), backend_factory=_fail_worker_initialization)
    with pytest.raises(ExecutionContextError):
        with planner:
            planner.plan(planner.initial_state(), requested_depth=planner.policy.depth)
    assert planner._closed
    assert not ({child.pid for child in multiprocessing.active_children()} - existing)


def test_unpicklable_worker_bootstrap_fails_typed_and_cleans_pool():
    from otqa.errors import ExecutionContextError
    from otqa.numerics.lp import LinearProgramBackend
    existing = {child.pid for child in multiprocessing.active_children()}
    # An internal injection can run locally yet cannot cross a spawn boundary.
    # Its failure must be reported without leaving a partly created pool.
    planner = PlannerSession(Problem(MATRIX), policy(),
        SolverExecution(2, multiprocessing.get_context("spawn")),
        backend_factory=lambda: LinearProgramBackend())
    with pytest.raises(ExecutionContextError):
        with planner:
            planner.plan(planner.initial_state(), requested_depth=planner.policy.depth)
    assert planner._closed
    assert not ({child.pid for child in multiprocessing.active_children()} - existing)


def test_idle_worker_registration_in_fresh_interpreter_imports_no_numerics():
    from pathlib import Path
    import subprocess
    import sys
    source = Path(__file__).resolve().parents[2] / "src"
    code = """
import sys
from otqa import Problem, AlgorithmPolicy, SingleCandidateStop, SolverExecution
from otqa.planning.session import _initialize_worker

def forbidden():
    raise AssertionError('idle registration called the numerical factory')

_initialize_worker(Problem([[1., 0.], [0., 1.]]),
    AlgorithmPolicy('fixed', 1, 'both', 5, 'candidate_count', SingleCandidateStop()),
    SolverExecution(8), None, forbidden, 'idle-owner')
assert 'numpy' not in sys.modules
assert 'scipy' not in sys.modules
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
        env=dict(os.environ, PYTHONPATH=str(source)), timeout=10)
    assert result.returncode == 0, result.stderr


def test_close_releases_own_prepared_state_cache_without_touching_other_session():
    first = PlannerSession(Problem(MATRIX), policy(depth=1), SolverExecution())
    second = PlannerSession(Problem(MATRIX), policy(depth=1), SolverExecution())
    try:
        first.initial_state()
        second_state = second.initial_state()
        assert first.states.cache.info().entries > 0
        other_entries = second.states.cache.info().entries
        first.close()
        assert first.states.cache.info().entries == 0
        assert second.states.cache.info().entries == other_entries
        assert not second.geometry.closed
        assert second.initial_state() is second_state
        assert second.plan(second_state, requested_depth=second.policy.depth).selected_plan.query is not None
    finally:
        first.close()
        second.close()
    assert second.states.cache.info().entries == 0
