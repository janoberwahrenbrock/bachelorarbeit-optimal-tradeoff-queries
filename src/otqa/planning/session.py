"""Session-owned exact fixed and adaptive planning.

Only independent root queries enter the optional process pool. Every child
search is serial, retains the complete allowed query set, and uses the
existing arithmetic order of its method. This module performs no file IO.
"""

from __future__ import annotations

from collections import OrderedDict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from concurrent.futures.process import BrokenProcessPool
from dataclasses import dataclass, replace
import math
import pickle
from typing import TYPE_CHECKING
import uuid

from otqa.config import VolumeConfidenceStop
from otqa.errors import ExecutionContextError
from otqa.models.core import AnsweredQuery, integer
from otqa.models.execution import HorizonSelectionEvidence, PlanningAttempt, ProgressEvidence

from .capture import EvaluationCaptureError, EvaluationCaptureOptions, TaskCapture, deliver
from .frontier import select_frontiers
from .models import (
    BranchEvaluation, Continuation, EfficiencyScore, FixedScore, HorizonEvidence,
    PlanningDecision, PolicyOption, QueryEvaluation, query_identity,
)

if TYPE_CHECKING:
    from otqa.config import AlgorithmPolicy, SolverExecution
    from otqa.models.core import Problem, Query
    from otqa.state import PreparedState


ANSWERS = ("<", "=", ">")


@dataclass(frozen=True, slots=True)
class _StatePlan:
    candidate_count: int
    is_feasible: bool
    value: float
    loss: float
    evaluation: QueryEvaluation | None = None
    evaluations: tuple[QueryEvaluation, ...] = ()
    expected_queries: float | None = None
    continuations: tuple[Continuation, ...] = ()
    generated_query_count: int = 0


@dataclass(frozen=True, slots=True)
class _Evaluated:
    evaluation: QueryEvaluation
    expected_queries: float | None = None
    continuations: tuple[Continuation, ...] = ()
    admissible: bool = True
    progress_witness: _Evaluated | None = None


@dataclass(frozen=True, slots=True)
class _RootTask:
    state: PreparedState
    query: Query
    source: str
    depth: int
    mode: str


@dataclass(frozen=True, slots=True)
class _CapturedRootTask(_RootTask):
    capture_address: tuple
    capture_limits: tuple[int, int]


_WORKER: PlannerSession | None = None
_WORKER_CONTEXT: tuple | None = None
_WORKER_FAILURE: ExecutionContextError | None = None


def _initialize_worker(problem, policy, execution, numerical_profile, backend_factory, session_id) -> None:
    global _WORKER_CONTEXT, _WORKER_FAILURE
    if _WORKER_CONTEXT is not None or _WORKER is not None:
        raise ExecutionContextError("root worker context is already registered")
    # Spawn can precede the first assigned task. Import process-local modules
    # now so a later state does not serialize cold NumPy/SciPy imports. Sessions,
    # backends, handles and finalizers still belong to the first actual task.
    _WORKER_CONTEXT = problem, policy, execution, numerical_profile, backend_factory, session_id
    try:
        from otqa.geometry import GeometrySession  # noqa: F401
        from otqa.state import StateEngine  # noqa: F401
    except Exception as error:
        # Preserve lazy task failure: an unused worker must not break its pool.
        _WORKER_FAILURE = ExecutionContextError("root worker session setup failed")
        _WORKER_FAILURE.__cause__ = error


def _run_worker(task: _RootTask):
    global _WORKER, _WORKER_FAILURE
    if _WORKER is None:
        if _WORKER_FAILURE is not None:
            raise _WORKER_FAILURE
        if _WORKER_CONTEXT is None:
            raise ExecutionContextError("root worker context has not been registered")
        problem, policy, execution, numerical_profile, backend_factory, session_id = _WORKER_CONTEXT
        worker = None
        try:
            from multiprocessing.util import Finalize
            worker = PlannerSession(problem, policy, replace(execution, workers=1), numerical_profile,
                backend_factory=backend_factory, _session_id=session_id, _worker=True)
            Finalize(worker, worker.close, exitpriority=10)
        except Exception as error:
            if worker is not None:
                try:
                    worker.close()
                except Exception as cleanup_error:
                    error.add_note(f"worker session cleanup also failed: {cleanup_error}")
            _WORKER_FAILURE = ExecutionContextError("root worker session setup failed")
            raise _WORKER_FAILURE from error
        _WORKER = worker
    result, blocks = _WORKER._execute_task(task)
    return (result, blocks) if isinstance(task, _CapturedRootTask) else result


def efficiency_key(pair: tuple[int, _Evaluated], root_count: int) -> tuple:
    horizon, result = pair
    loss = result.evaluation.expected_terminal_loss
    if loss is None:
        loss = result.evaluation.expected_terminal_candidates
    assert result.expected_queries is not None
    return (-(float(root_count) - loss) / result.expected_queries,
            result.expected_queries, horizon, *query_identity(result.evaluation.query))


class PlannerSession:
    """Own numerical handles, prepared states, root pool and bounded caches."""

    def __init__(self, problem: Problem, policy: AlgorithmPolicy, execution: SolverExecution,
                 numerical_profile=None, *, backend_factory=None,
                 evaluation_capture: EvaluationCaptureOptions | None = None,
                 _session_id: str | None = None, _worker: bool = False):
        from otqa.geometry import GeometrySession
        from otqa.state import StateEngine

        # Reserve separately for worker collection, serialized transport,
        # completed parent futures, and synchronous delivery validation.
        # Bounding submissions alone would ignore those simultaneous copies.
        if evaluation_capture is not None and 4 * execution.workers * evaluation_capture.max_task_bytes > min(
            evaluation_capture.max_pending_bytes, evaluation_capture.max_session_bytes,
        ):
            raise ValueError("capture budgets cannot hold all outstanding root tasks")
        self.problem, self.policy, self.execution = problem, policy, execution
        self.numerical_profile = numerical_profile
        self._backend_factory = backend_factory
        self._session_id = _session_id or uuid.uuid4().hex
        self.geometry = GeometrySession(numerical_profile, backend_factory=backend_factory)
        self.states = StateEngine(problem, policy, self.geometry, session_id=self._session_id)
        self._executor: ProcessPoolExecutor | None = None
        self._closed = False
        self._worker = _worker
        self._capture_options = evaluation_capture
        self._capture: TaskCapture | None = None
        self._observation_ordinal = 0
        self._plan_index = 0
        self._plan_address: tuple | None = None
        self._task_counter = 0
        self._plan_cache: OrderedDict[tuple, PlanningAttempt] = OrderedDict()
        self._captured_plans = {} if evaluation_capture is not None else None

    def _check_open(self) -> None:
        if self._closed:
            raise RuntimeError("planner session is closed")

    def initial_state(self, answers=()):
        self._check_open()
        return self.states.initial(tuple(answers), need_volumes=True)

    def advance(self, state: PreparedState, answered_query: AnsweredQuery):
        self._check_open()
        return self.states.advance(state, answered_query, need_volumes=True, actual=True)

    def analyze(self, state: PreparedState, *, volumes: bool = True):
        """Return the public immutable analysis, keeping prepared state internal."""
        from otqa.models.results import StateAnalysis
        self._check_open()
        state = self.states.ensure_analysis(state, ratios=True, volumes=volumes)
        analysis = state.analysis
        return StateAnalysis(
            answered_total=len(state.history),
            candidate_indices=tuple(analysis.candidates) if analysis is not None else (),
            candidate_volumes=tuple((int(i), float(v)) for i, v in (analysis.candidate_volumes or {}).items()) if analysis else (),
            candidate_volume_shares=tuple((int(i), float(v)) for i, v in (analysis.candidate_volume_shares or {}).items()) if analysis else (),
            feasible=state.is_feasible,
        )

    @property
    def _stop_aware(self) -> bool:
        return self.policy.planning_evaluation == "stop_aware"

    @property
    def _need_planning_volumes(self) -> bool:
        return self._stop_aware and isinstance(self.policy.stopping, VolumeConfidenceStop)

    @property
    def _capturing(self) -> bool:
        return self._capture is not None or self._capture_options is not None

    def _status(self, state: PreparedState) -> tuple[str | None, float | None]:
        analysis = state.analysis
        count = len(analysis.candidates)
        shares = analysis.candidate_volume_shares
        maximum = max(float(shares[i]) for i in analysis.candidates) if shares is not None and count else None
        if count == 1:
            return "single_candidate", maximum
        if self._need_planning_volumes and maximum is not None and maximum >= self.policy.stopping.threshold:
            return "volume_confidence", maximum
        return None, maximum

    def _observe(self, kind: str, state: PreparedState, depth: int, value: object,
                 *, query=None, answer=None, not_computed=None) -> None:
        if self._capture is None and self._capture_options is None:
            return
        address = (self._session_id, tuple((query_identity(item.query), item.answer) for item in state.history),
                   depth, query_identity(query) if query is not None else None, answer)
        if self._capture is None:
            # Inventories and lazy-refinement boundaries are evaluated in the
            # parent outside an individual root task and are delivered at once.
            options = self._capture_options
            collector = TaskCapture(self._plan_address, ("parent_observation", self._task_counter),
                                    options.max_block_bytes, options.max_task_bytes)
            self._task_counter += 1
            collector.observe(kind, address, 0, value, not_computed=not_computed)
            deliver(options, collector.finish())
            return
        self._capture.observe(kind, address, self._observation_ordinal, value, not_computed=not_computed)
        self._observation_ordinal += 1

    def _parent_observation(self, phase: str, state: PreparedState, value: object) -> None:
        options = self._capture_options
        if options is None:
            return
        collector = TaskCapture(self._plan_address, ("parent", phase), options.max_block_bytes, options.max_task_bytes)
        collector.observe("cache" if phase == "cache" else "plan_boundary",
                          (self._session_id, self._plan_index, phase), 0, value)
        deliver(options, collector.finish())

    def _queries(self, state: PreparedState, depth: int):
        from otqa.queries import generate_queries
        if self._capture is None and self._capture_options is None:
            data = generate_queries(state, depth)
        else:
            def record_filter(reason, query, retained):
                self._observe("candidate_inventory", state, depth, ("filter", reason, query, retained), query=query)

            data = generate_queries(state, depth, capture_filter=record_filter)
        self._observe("candidate_inventory", state, depth, data.query_candidates)
        return data

    def _child(self, state: PreparedState, query: Query, answer: str, probability: float,
               *, terminal: bool, volumes: bool, recovered: bool = False):
        return self.states.advance(state, AnsweredQuery(query, answer), terminal=terminal,
                                   need_volumes=volumes, probability=probability, recovered=recovered)

    def _evaluate_count(self, state: PreparedState, query: Query, depth: int, source: str,
                        *, retain_continuations: bool = False) -> _Evaluated:
        """Ordinary fixed arithmetic deliberately accumulates with ordered +=."""
        probabilities = self.geometry.probabilities(state.weight_space, query)
        branches: list[BranchEvaluation] = []
        continuations: list[Continuation] = []
        expected = 0.0
        for answer in ANSWERS:
            probability = probabilities[answer]
            if probability == 0.0:
                branches.append(BranchEvaluation(answer, probability, 0.0, None, False))
                continue
            if depth == 1:
                from otqa.state.analysis import compute_terminal_candidate_count
                count, feasible = compute_terminal_candidate_count(state, query, answer, probability,
                    recovered=bool(getattr(probabilities, "recovered_exact_partition", False)))
                value = float(count)
            else:
                child = self._child(state, query, answer, probability, terminal=False, volumes=False,
                    recovered=bool(getattr(probabilities, "recovered_exact_partition", False)))
                planned = self._fixed(child, depth - 1)
                count, feasible, value = planned.candidate_count, planned.is_feasible, planned.value
                if retain_continuations:
                    continuations.append(Continuation(answer, probability, count, value, planned.evaluation))
            expected += probability * value
            branches.append(BranchEvaluation(answer, probability, value, count, feasible))
        evaluation = QueryEvaluation(query, expected, tuple(branches), source)
        self._observe("root_evaluation", state, depth, evaluation, query=query)
        cost = None
        if retain_continuations:
            cost = 1.0 + math.fsum(child.probability for child in continuations if child.evaluation is not None)
        return _Evaluated(evaluation, cost, tuple(continuations))

    def _evaluate_stop(self, state: PreparedState, query: Query, depth: int, source: str) -> _Evaluated:
        probabilities = self.geometry.probabilities(state.weight_space, query)
        branches: list[BranchEvaluation] = []
        continuations: list[Continuation] = []
        for answer in ANSWERS:
            probability = probabilities[answer]
            if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
                raise RuntimeError("invalid branch probability in stop-aware plan")
            if probability == 0.0:
                branches.append(BranchEvaluation(answer, probability, 0.0, None, False, 0.0,
                                                 expected_followup_queries=0.0))
                continue
            child = self._child(state, query, answer, probability, terminal=depth == 1,
                                volumes=self._need_planning_volumes, recovered=depth in (1, 2))
            if not child.is_feasible or not child.analysis.candidates:
                raise RuntimeError("positive-probability branch has no valid candidates in stop-aware plan")
            count = len(child.analysis.candidates)
            reason, maximum = self._status(child)
            continuation = None
            if depth > 1 and reason is None:
                continuation = self._fixed_stop(child, depth - 1)
            selected = continuation.evaluation if continuation else None
            value = continuation.value if continuation else float(count)
            loss = continuation.loss if continuation else 1.0 if reason else float(count)
            followups = (float(selected is not None) if depth == 2 else
                         float(continuation.expected_queries or 0.0) if continuation else 0.0)
            branches.append(BranchEvaluation(answer, probability, value, count, True, loss, reason, maximum, followups))
            if depth == 2:
                continuations.append(Continuation(answer, probability, count, value, selected,
                    loss, reason, maximum))
        evaluation = QueryEvaluation(query,
            math.fsum(branch.probability * branch.expected_terminal_candidates for branch in branches),
            tuple(branches), source,
            expected_terminal_loss=math.fsum(branch.probability * branch.expected_terminal_loss for branch in branches))
        cost = 1.0 + math.fsum(branch.probability * branch.expected_followup_queries for branch in branches)
        self._validate(evaluation, stop_aware=True, max_followups=depth - 1)
        if not math.isfinite(cost) or not 1.0 <= cost <= depth + 1e-12:
            raise RuntimeError("invalid expected question count in stop-aware plan")
        children = tuple(continuations)
        if self._capturing:
            self._observe("root_evaluation", state, depth, (evaluation, cost, children), query=query)
        return _Evaluated(evaluation, cost, children)

    def _fixed(self, state: PreparedState, depth: int, *, root: bool = False) -> _StatePlan:
        state = self.states.ensure_analysis(state, ratios=True, volumes=False)
        if not state.is_feasible:
            return _StatePlan(0, False, 0.0, 0.0)
        count = len(state.analysis.candidates)
        if depth == 0 or count <= 1:
            return _StatePlan(count, True, float(count), float(count))
        data = self._queries(state, depth)
        if not data.query_candidates:
            return _StatePlan(count, True, float(count), float(count))
        results = self._evaluate_many(state, data, depth, "count", root=root)
        evaluations = tuple(result.evaluation for result in results)
        profiles = [[item.expected_terminal_candidates] for item in evaluations]
        best_value = min(profile[0] for profile in profiles)
        tied = [i for i, profile in enumerate(profiles) if profile[0] == best_value]
        for shallower in range(depth - 1, 0, -1):
            if len(tied) <= 1:
                self._observe("root_evaluation", state, shallower, None,
                              not_computed="lazy_refinement_not_required")
                break
            shallow = self._evaluate_many(state, data, shallower, "count", root=root,
                                          queries=tuple(evaluations[i].query for i in tied))
            for index, result in zip(tied, shallow, strict=True):
                profiles[index].append(result.evaluation.expected_terminal_candidates)
            minimum = min(profiles[index][-1] for index in tied)
            tied = [index for index in tied if profiles[index][-1] == minimum]
        refined = tuple(replace(item, lexicographic_profile=tuple(profiles[index]))
                        for index, item in enumerate(evaluations))
        index = min(tied, key=lambda i: query_identity(refined[i].query))
        chosen = refined[index]
        if chosen.expected_terminal_candidates < 1.0 - 1e-9:
            raise RuntimeError("expected candidate count must not be below one for a feasible state with candidates")
        if self._capturing:
            self._observe("combination_choice", state, depth, ("fixed_selection", chosen), query=chosen.query)
        return _StatePlan(count, True, chosen.expected_terminal_candidates,
                          chosen.expected_terminal_candidates, chosen, refined,
                          generated_query_count=len(data.query_candidates))

    def _fixed_stop(self, state: PreparedState, depth: int, *, root: bool = False) -> _StatePlan:
        state = self.states.ensure_analysis(state, ratios=True, volumes=self._need_planning_volumes)
        if not state.is_feasible:
            return _StatePlan(0, False, 0.0, 0.0, expected_queries=0.0)
        count = len(state.analysis.candidates)
        reason, _ = self._status(state)
        if depth == 0 or count <= 1 or reason:
            return _StatePlan(count, True, float(count), 1.0 if reason else float(count), expected_queries=0.0)
        data = self._queries(state, depth)
        if not data.query_candidates:
            return _StatePlan(count, True, float(count), float(count), expected_queries=0.0)
        results = self._evaluate_many(state, data, depth, "stop", root=root)
        selected = min(results, key=lambda result: (
            result.evaluation.expected_terminal_loss, *query_identity(result.evaluation.query)))
        evaluation = selected.evaluation
        if self._capturing:
            self._observe("combination_choice", state, depth,
                ("stop_selection", evaluation, selected.expected_queries), query=evaluation.query)
        return _StatePlan(count, True, evaluation.expected_terminal_candidates,
                          evaluation.expected_terminal_loss, evaluation,
                          tuple(item.evaluation for item in results), selected.expected_queries,
                          selected.continuations, len(data.query_candidates))

    def _child_frontier(self, state: PreparedState) -> tuple[PolicyOption, ...]:
        count = len(state.analysis.candidates)
        reason, maximum = self._status(state) if self._stop_aware else ("single_candidate" if count == 1 else None, None)
        if reason:
            options = (PolicyOption(None, float(count), 1.0, 0.0, stop_reason=reason, maximum_volume_share=maximum),)
            self._observe("child_options", state, 2, options)
            return options
        data = self._queries(state, 2)
        if not data.query_candidates:
            options = (PolicyOption(None, float(count), float(count), 0.0, maximum_volume_share=maximum),)
            self._observe("child_options", state, 2, options)
            return options
        results = self._evaluate_many(state, data, 2, "efficiency", root=False)
        options = tuple(PolicyOption(item.evaluation, item.evaluation.expected_terminal_candidates,
            item.evaluation.expected_terminal_loss if self._stop_aware else item.evaluation.expected_terminal_candidates,
            item.expected_queries, item.continuations, maximum_volume_share=maximum) for item in results)
        # Preserve raw complete H2 options until global gain-sign admission is
        # known. Child pruning cannot run first on the all-negative path.
        self._observe("child_options", state, 2, options)
        return options

    def _evaluate_h3(self, state: PreparedState, query: Query, source: str) -> _Evaluated:
        probabilities = self.geometry.probabilities(state.weight_space, query)
        if any(not math.isfinite(p) or not 0.0 <= p <= 1.0 for p in probabilities.values()) or not math.isclose(
            math.fsum(probabilities[answer] for answer in ANSWERS), 1.0, abs_tol=1e-12, rel_tol=0.0):
            raise RuntimeError("invalid branch probabilities in horizon-three plan")
        children, frontiers = [], []
        for answer in ANSWERS:
            probability = probabilities[answer]
            if probability == 0.0:
                continue
            child = self._child(state, query, answer, probability, terminal=False,
                                volumes=self._need_planning_volumes, recovered=True)
            if not child.is_feasible or not child.analysis.candidates:
                raise RuntimeError("positive-probability branch has no valid candidates in horizon-three plan")
            children.append((answer, probability, child))
            frontiers.append(self._child_frontier(child))
        observe = (lambda kind, value: self._observe(kind, state, 3, value, query=query)) if self._capture else None
        child_observers = tuple(
            (lambda kind, value, child=child: self._observe(kind, child, 2, value))
            for _, _, child in children) if self._capturing else None
        selection = select_frontiers(len(state.analysis.candidates), tuple(item[1] for item in children),
            tuple(frontiers), minimum=self.policy.min_expected_progress, observe=observe,
            child_observers=child_observers)
        witness = self._assemble_h3(state, query, source, probabilities, children, selection.best_progress_witness)
        if selection.selected is None:
            return replace(witness, admissible=False, progress_witness=witness)
        selected = (witness if selection.selected == selection.best_progress_witness else
                    self._assemble_h3(state, query, source, probabilities, children, selection.selected))
        return replace(selected, progress_witness=witness)

    def _assemble_h3(self, state, query, source, probabilities, children, chosen):
        by_answer = {item[0]: (item[2], option) for item, option in zip(children, chosen, strict=True)}
        branches, continuations = [], []
        for answer in ANSWERS:
            probability = probabilities[answer]
            if probability == 0.0:
                branches.append(BranchEvaluation(answer, probability, 0.0, None, False,
                    0.0 if self._stop_aware else None,
                    expected_followup_queries=0.0 if self._stop_aware else None))
                continue
            child, option = by_answer[answer]
            count = len(child.analysis.candidates)
            branches.append(BranchEvaluation(answer, probability, option.expected_terminal_candidates, count, True,
                option.expected_terminal_loss if self._stop_aware else None,
                option.stop_reason if self._stop_aware else None,
                option.maximum_volume_share if self._stop_aware else None,
                option.expected_queries if self._stop_aware else None))
            continuations.append(Continuation(answer, probability, count, option.expected_terminal_candidates,
                option.evaluation, option.expected_terminal_loss if self._stop_aware else None,
                option.stop_reason, option.maximum_volume_share, option.expected_queries, option.continuations))
        evaluation = QueryEvaluation(query,
            math.fsum(branch.probability * branch.expected_terminal_candidates for branch in branches),
            tuple(branches), source,
            expected_terminal_loss=math.fsum(branch.probability * branch.expected_terminal_loss for branch in branches) if self._stop_aware else None)
        cost = 1.0 + math.fsum(child.probability * child.expected_queries for child in continuations)
        self._validate(evaluation, stop_aware=self._stop_aware, max_followups=2)
        if not math.isfinite(cost) or not 1.0 <= cost <= 3.0 + 1e-12:
            raise RuntimeError("invalid expected question count in horizon-three plan")
        children = tuple(continuations)
        if self._capturing:
            self._observe("root_evaluation", state, 3, (evaluation, cost, children), query=query)
        return _Evaluated(evaluation, cost, children)

    @staticmethod
    def _validate(evaluation: QueryEvaluation, *, stop_aware: bool = False, max_followups: int = 1) -> None:
        for branch in evaluation.branches:
            if not math.isfinite(branch.probability) or not 0.0 <= branch.probability <= 1.0:
                raise RuntimeError("invalid branch probability in query-efficiency plan")
            if branch.probability > 0.0 and (not branch.is_feasible or branch.candidate_count is None
                or branch.candidate_count <= 0 or not math.isfinite(branch.expected_terminal_candidates)
                or branch.expected_terminal_candidates < 1.0 - 1e-9):
                raise RuntimeError("positive-probability branch has no valid candidates in query-efficiency plan")
            if stop_aware:
                followups = branch.expected_followup_queries
                if followups is None or not math.isfinite(followups) or not 0.0 <= followups <= max_followups:
                    raise RuntimeError("inconsistent stop-aware branch metadata")
                if max_followups == 1 and followups not in (0, 1):
                    raise RuntimeError("inconsistent stop-aware branch metadata")
                if branch.probability <= 0.0:
                    continue
                loss = branch.expected_terminal_loss
                if loss is None or not math.isfinite(loss) or not 1.0 - 1e-9 <= loss <= branch.candidate_count + 1e-9 or loss > branch.expected_terminal_candidates + 1e-9:
                    raise RuntimeError("invalid stop-aware terminal loss")
                maximum = branch.maximum_volume_share
                if maximum is not None and (not math.isfinite(maximum) or not 0.0 <= maximum <= 1.0 + 1e-12):
                    raise RuntimeError("invalid stop-aware maximum candidate volume share")
                if branch.stop_reason is not None and (
                    branch.stop_reason not in ("single_candidate", "volume_confidence") or followups != 0
                    or loss != 1.0 or branch.expected_terminal_candidates != float(branch.candidate_count)
                    or (branch.stop_reason == "single_candidate" and branch.candidate_count != 1)):
                    raise RuntimeError("invalid absorbing stop-aware branch")
        if not math.isclose(math.fsum(item.probability for item in evaluation.branches), 1.0, abs_tol=1e-12, rel_tol=0.0):
            raise RuntimeError("query-efficiency branch probabilities do not sum to one")
        expected = math.fsum(item.probability * item.expected_terminal_candidates for item in evaluation.branches if item.probability > 0.0)
        if not math.isfinite(evaluation.expected_terminal_candidates) or not math.isclose(expected,
            evaluation.expected_terminal_candidates, abs_tol=1e-12, rel_tol=1e-12):
            raise RuntimeError("inconsistent query-efficiency terminal expectation")
        if stop_aware:
            loss = math.fsum(item.probability * item.expected_terminal_loss for item in evaluation.branches if item.probability > 0.0)
            if not math.isfinite(evaluation.expected_terminal_loss) or not math.isclose(loss,
                evaluation.expected_terminal_loss, abs_tol=1e-12, rel_tol=1e-12):
                raise RuntimeError("inconsistent stop-aware terminal loss expectation")

    def _evaluate_one(self, state: PreparedState, query: Query, depth: int, source: str, mode: str) -> _Evaluated:
        if mode == "count":
            return self._evaluate_count(state, query, depth, source)
        if mode == "stop":
            return self._evaluate_stop(state, query, depth, source)
        if depth == 3:
            return self._evaluate_h3(state, query, source)
        result = (self._evaluate_stop(state, query, depth, source) if self._stop_aware else
                  self._evaluate_count(state, query, depth, source, retain_continuations=depth == 2))
        self._validate(result.evaluation)
        if result.expected_queries is None:
            result = replace(result, expected_queries=1.0)
        if not math.isfinite(result.expected_queries) or not 1.0 <= result.expected_queries <= depth + 1e-12:
            raise RuntimeError("invalid expected question count in query-efficiency plan")
        return result

    def _execute_task(self, task: _RootTask) -> tuple[_Evaluated, tuple]:
        if self._worker:
            try:
                state = self.states.bind(task.state)
            except Exception as error:
                raise ExecutionContextError("root worker state binding failed") from error
        else:
            # Serial parent evaluations already use this session's handles.
            # Only an actual process transfer requires numerical rebinding.
            self.states.check(task.state)
            state = task.state
        previous = self._capture
        captured = isinstance(task, _CapturedRootTask)
        if captured:
            self._capture = TaskCapture(task.capture_address[0], task.capture_address[1], *task.capture_limits)
            self._observation_ordinal = 0
        try:
            result = self._evaluate_one(state, task.query, task.depth, task.source, task.mode)
            blocks = self._capture.finish() if captured else ()
            return result, blocks
        except Exception as error:
            if captured:
                # Retain the mathematical exception and every completed
                # diagnostic block. A failed task never produces a plan end.
                if not isinstance(error, EvaluationCaptureError):
                    try:
                        self._capture.observe("error", (self._session_id, task.capture_address[1]),
                            self._observation_ordinal, (type(error).__qualname__, str(error)))
                    except EvaluationCaptureError:
                        pass
                error.evaluation_capture_blocks = tuple(self._capture.blocks)
                error.evaluation_capture_complete = False
            raise
        finally:
            self._capture = previous

    @staticmethod
    def _receive(call, options):
        try:
            return call()
        except Exception as error:
            if options is not None:
                blocks = getattr(error, "evaluation_capture_blocks", ())
                if blocks:
                    deliver(options, blocks, complete=False)
            if isinstance(error, (BrokenProcessPool, pickle.PicklingError)):
                raise ExecutionContextError("root worker process pool or task transfer failed") from error
            raise

    def _pool(self) -> ProcessPoolExecutor:
        if self._executor is None:
            try:
                self._executor = ProcessPoolExecutor(max_workers=self.execution.workers,
                    mp_context=self.execution.multiprocessing_context,
                    initializer=_initialize_worker,
                    initargs=(self.problem, self.policy, self.execution, self.numerical_profile,
                              self._backend_factory, self._session_id))
            except Exception as error:
                raise ExecutionContextError("root worker pool setup failed") from error
        return self._executor

    @staticmethod
    def _submit(pool, task):
        try:
            return pool.submit(_run_worker, task)
        except Exception as error:
            raise ExecutionContextError("root worker task submission failed") from error

    def _evaluate_many(self, state: PreparedState, data, depth: int, mode: str, *, root: bool,
                       queries: tuple | None = None) -> tuple[_Evaluated, ...]:
        from otqa.queries import canonical_key
        queries = data.query_candidates if queries is None else queries
        if not root:
            return tuple(self._evaluate_one(state, query, depth,
                data.query_sources.get(canonical_key(query), "unknown"), mode) for query in queries)
        options = self._capture_options if root else None
        tasks = []
        for query in queries:
            capture_address = None
            if options is not None:
                capture_address = self._plan_address, ("root", self._task_counter, depth, query_identity(query))
                self._task_counter += 1
            arguments = (state, query, data.query_sources.get(canonical_key(query), "unknown"), depth, mode)
            tasks.append(_CapturedRootTask(*arguments, capture_address, (options.max_block_bytes, options.max_task_bytes))
                         if options is not None else _RootTask(*arguments))
        if not root or self.execution.workers == 1 or len(tasks) <= 1:
            results = []
            for task in tasks:
                if root:
                    result, blocks = self._receive(lambda: self._execute_task(task), options)
                    if options is not None:
                        deliver(options, blocks)
                else:
                    result = self._evaluate_one(state, task.query, depth, task.source, mode)
                results.append(result)
            return tuple(results)
        # Refill a completed slot even when an earlier query is still running.
        # Only mathematical values remain in this inventory-ordered array;
        # capture payloads are delivered and released before another submit.
        pool, pending = self._pool(), {}
        results, errors = [None] * len(tasks), {}
        next_index = 0

        def submit_next():
            nonlocal next_index
            index = next_index
            next_index += 1
            try:
                pending[self._submit(pool, tasks[index])] = index
            except Exception as error:
                errors[index] = error

        try:
            for _ in range(min(self.execution.workers, len(tasks))):
                submit_next()
                if errors:
                    break
            while pending:
                completed, _ = wait(pending, return_when=FIRST_COMPLETED)
                while completed:
                    # Several errors can become ready together. Inspect them
                    # in logical order rather than choosing by delivery time.
                    future = min(completed, key=pending.__getitem__)
                    completed.remove(future)
                    index = pending.pop(future)
                    try:
                        received = self._receive(future.result, options)
                        if options is not None:
                            result, blocks = received
                            deliver(options, blocks)
                            results[index] = result
                            del result, blocks
                        else:
                            results[index] = received
                        del received
                    except EvaluationCaptureError:
                        # A failed sink invalidates capture immediately.
                        raise
                    except Exception as error:
                        errors[index] = error
                        if options is not None and hasattr(error, "evaluation_capture_blocks"):
                            # _receive has synchronously delivered these blocks.
                            # Retaining them on a deferred mathematical error
                            # would exceed the bounded capture transport scope.
                            error.evaluation_capture_blocks = ()
                            error.evaluation_capture_delivered = True
                    finally:
                        # Future._result owns the transport tuple until this
                        # final reference is removed. Do so before refilling.
                        del future
                    if errors:
                        earliest_error = min(errors)
                        for outstanding in tuple(pending):
                            if pending[outstanding] > earliest_error and outstanding.cancel():
                                pending.pop(outstanding)
                    elif next_index < len(tasks):
                        submit_next()
            if errors:
                # Earlier pending tasks have also been inspected, preserving
                # inventory-order mathematical error priority.
                raise errors[min(errors)]
        except BaseException as error:
            for future in pending:
                future.cancel()
            try:
                pool.shutdown(wait=True, cancel_futures=True)
            except BaseException as cleanup_error:
                error.add_note(f"root pool cleanup also failed: {cleanup_error}")
            finally:
                self._executor = None
            raise
        return tuple(results)

    def _progress(self, count: int, evaluation: QueryEvaluation) -> ProgressEvidence:
        terminal = (evaluation.expected_terminal_loss if self._stop_aware and
                    evaluation.expected_terminal_loss is not None else evaluation.expected_terminal_candidates)
        gain = float(count) - terminal
        threshold = self.policy.min_expected_progress
        return ProgressEvidence(
            basis="effective_loss" if self._stop_aware else "candidate_count",
            starting_value=float(count), expected_terminal_value=terminal,
            expected_progress=gain, threshold=threshold,
            admissible=threshold is None or gain > threshold)

    def _efficiency_decision(self, depth: int, result: _Evaluated, count: int) -> PlanningDecision:
        evaluation = result.evaluation
        loss = (evaluation.expected_terminal_loss if evaluation.expected_terminal_loss is not None
                else evaluation.expected_terminal_candidates)
        gain, cost = float(count) - loss, result.expected_queries
        if cost is None or not math.isfinite(cost) or cost <= 0 or not math.isfinite(gain) or not math.isfinite(gain / cost):
            raise RuntimeError("nonfinite query-efficiency score or invalid query cost")
        if loss < 1.0 - 1e-9 or gain < -1e-9:
            raise RuntimeError("terminal candidate expectation is outside feasible query-efficiency bounds")
        score = EfficiencyScore(evaluation.expected_terminal_candidates, loss, cost, gain, gain / cost)
        return PlanningDecision(evaluation.query, depth, score,
            tuple((item.answer, item.probability) for item in evaluation.branches),
            evaluation, result.continuations)

    def plan(self, state: PreparedState, *, requested_depth: int) -> PlanningAttempt:
        """Evaluate an explicit mathematical request, without execution phase.

        Policy and threshold are immutable session inputs; history and requested
        depth identify the reusable result. Countdown cursors stay in the caller.
        """
        from otqa.state import history_key
        self._check_open()
        requested_depth = integer(requested_depth, name="requested_depth", minimum=1)
        if requested_depth > self.policy.depth:
            raise ValueError("requested depth exceeds the configured maximum")
        state = self.states.bind(state)
        state = self.states.ensure_analysis(state, ratios=True, volumes=self._need_planning_volumes)
        self._task_counter = 0
        if self._capture_options is not None:
            self._plan_index += 1
            self._plan_address = (self._session_id, self._plan_index)
            self._parent_observation("begin", state, (state.analysis, self.policy.query_strategy, requested_depth))
        key = (history_key(state.history), requested_depth)
        if key in self._plan_cache:
            choice = self._plan_cache[key]
            self._plan_cache.move_to_end(key)
            if self._capture_options is not None:
                self._parent_observation("cache", state, ("reused_plan", self._captured_plans[key]))
            self._parent_observation("end", state, choice)
            return choice
        count = len(state.analysis.candidates) if state.analysis else 0
        depths = ((requested_depth,) if self.policy.query_strategy == "fixed" else
                  tuple(range(1, requested_depth + 1)))
        horizon_selections, mathematical_horizons = [], []
        candidates, witnesses = [], []
        if not state.is_feasible or count <= 1 or (self._stop_aware and self._status(state)[0] is not None):
            horizon_selections = [HorizonSelectionEvidence(depth, 0, 0, "no_query") for depth in depths]
        elif self.policy.query_strategy == "fixed":
            # Fixed singleton stop-aware planning retains its ordinary route.
            planned = (self._fixed_stop(state, requested_depth, root=True) if self._need_planning_volumes else
                       self._fixed(state, requested_depth, root=True))
            evaluation = planned.evaluation
            if evaluation is None:
                horizon_selections.append(HorizonSelectionEvidence(requested_depth,
                    planned.generated_query_count, len(planned.evaluations), "no_query"))
            else:
                score = FixedScore(planned.value, planned.loss,
                    evaluation.lexicographic_profile or (evaluation.expected_terminal_candidates,), planned.expected_queries)
                probabilities = tuple((branch.answer, branch.probability) for branch in evaluation.branches)
                mathematical = HorizonEvidence(requested_depth, planned.evaluations, evaluation.query,
                    score, probabilities, planned.continuations)
                decision = PlanningDecision(evaluation.query, requested_depth, score, probabilities, evaluation,
                    planned.continuations, (mathematical,))
                progress = self._progress(count, evaluation)
                witnesses.append(decision)
                if progress.admissible:
                    candidates.append(decision)
                horizon_selections.append(HorizonSelectionEvidence(requested_depth,
                    planned.generated_query_count, len(planned.evaluations),
                    "available" if progress.admissible else "insufficient_expected_progress",
                    decision if progress.admissible else None, progress if progress.admissible else None,
                    decision, progress))
        else:
            for depth in depths:
                data = self._queries(state, depth)
                results = self._evaluate_many(state, data, depth, "efficiency", root=True)
                plans, progress_plans = [], []
                for result in results:
                    decision = self._efficiency_decision(depth, result, count)
                    progress = self._progress(count, decision.evaluation)
                    if result.admissible and progress.admissible:
                        plans.append((result, decision))
                    witness_result = result.progress_witness or result
                    witness = (decision if witness_result is result else
                               self._efficiency_decision(depth, witness_result, count))
                    progress_plans.append((witness_result, witness))
                    if self._capture_options is not None:
                        self._observe("root_evaluation", state, depth,
                            ("efficiency_score", decision.query, decision.score), query=decision.query)
                selected = min(plans, key=lambda item: efficiency_key((depth, item[0]), count)) if plans else None
                best = min(progress_plans, key=lambda item: (
                    -self._progress(count, item[1].evaluation).expected_progress,
                    efficiency_key((depth, item[0]), count))) if progress_plans else None
                mathematical_horizons.append(HorizonEvidence(depth, tuple(item.evaluation for item in results),
                    selected[1].query if selected else None, selected[1].score if selected else None,
                    selected[1].answer_probabilities if selected else (), selected[1].continuations if selected else ()))
                if selected:
                    candidates.append(selected[1])
                if best:
                    witnesses.append(best[1])
                outcome = "available" if selected else "insufficient_expected_progress" if best else "no_query"
                horizon_selections.append(HorizonSelectionEvidence(depth, len(data.query_candidates), len(results), outcome,
                    selected[1] if selected else None,
                    self._progress(count, selected[1].evaluation) if selected else None,
                    best[1] if best else None,
                    self._progress(count, best[1].evaluation) if best else None))
            if mathematical_horizons:
                candidates = [replace(item, horizons=tuple(mathematical_horizons)) for item in candidates]
                witnesses = [replace(item, horizons=tuple(mathematical_horizons)) for item in witnesses]
                horizon_selections = [replace(item,
                    selected_plan=replace(item.selected_plan, horizons=tuple(mathematical_horizons)) if item.selected_plan else None,
                    best_progress_witness=replace(item.best_progress_witness, horizons=tuple(mathematical_horizons))
                        if item.best_progress_witness else None) for item in horizon_selections]
        def decision_key(item):
            if isinstance(item.score, EfficiencyScore):
                return (-item.score.rate, item.score.expected_queries, item.horizon, *query_identity(item.query))
            return (*item.score.lexicographic_profile, *query_identity(item.query))
        selected = min(candidates, key=decision_key) if candidates else None
        witness = min(witnesses, key=lambda item: (
            -self._progress(count, item.evaluation).expected_progress,
            decision_key(item) if isinstance(item.score, EfficiencyScore) else query_identity(item.query))) if witnesses else None
        outcome = "available" if selected else "insufficient_expected_progress" if witness else "no_query"
        choice = PlanningAttempt(requested_depth, depths, outcome, selected,
            self._progress(count, selected.evaluation) if selected else None,
            witness, tuple(horizon_selections))
        self._plan_cache[key] = choice
        if self._capture_options is not None:
            self._captured_plans[key] = self._plan_address
        while len(self._plan_cache) > 16:
            evicted, _ = self._plan_cache.popitem(last=False)
            if self._capture_options is not None:
                self._captured_plans.pop(evicted, None)
        self._parent_observation("end", state, choice)
        return choice

    def close(self) -> None:
        if self._closed:
            return
        try:
            if self._executor is not None:
                self._executor.shutdown(wait=True, cancel_futures=True)
        finally:
            try:
                self.geometry.close()
            finally:
                try:
                    self.states.cache.clear()
                finally:
                    self._plan_cache.clear()
                    if self._captured_plans is not None:
                        self._captured_plans.clear()
                    self._closed = True

    def __enter__(self):
        self._check_open()
        return self

    def __exit__(self, *_):
        self.close()
