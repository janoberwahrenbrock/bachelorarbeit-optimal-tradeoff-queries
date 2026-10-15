"""Bound states and reusable candidate analyses for one solver session."""
from __future__ import annotations

from dataclasses import replace
import struct
from uuid import uuid4

from otqa.geometry import ConstraintSystem
from otqa.geometry.rational import RecoveryNotApplicable, RecoveryGeometryError, recover_strict_singleton
from otqa.models import AnsweredQuery
from otqa.numerics.cache import BoundedCache
from .types import CandidateAnalysis, GoalPairRatioIntervals, PreparedState
from .frozen import FrozenMapping
from .ratios import candidate_interval, feasible, from_vertices, infeasible_interval, ordered_pairs, positive_width, supports, terminal_membership


def candidate_analysis(problem, system, geometry, candidate_subset=None, *, ratios=True, volumes=False):
    checked = tuple(range(problem.alternative_count)) if candidate_subset is None else tuple(candidate_subset)
    if not checked:
        return CandidateAnalysis((), () if ratios else None, {}, {})
    pairs = ordered_pairs(problem.objective_count)
    intervals = {pair: {} for pair in pairs} if ratios else None
    volume_values = {} if volumes else None
    feasible_set, relevant = set(), set()
    for candidate in checked:
        if not 0 <= candidate < problem.alternative_count:
            raise IndexError("candidate index out of range")
        region = geometry.optimality_region(problem, system, candidate)
        polytope = geometry.vertices(region)
        corrected = False
        if volumes:
            value = geometry.volume_from_vertices(region, polytope)
            volume_values[candidate] = value
            corrected = bool(getattr(value, "exact_positive_correction", False))
        good_geometry = polytope.status in {"full_dimensional", "point"} and not corrected
        if good_geometry and not ratios:
            is_feasible, has_width = terminal_membership(polytope.vertices, problem.objective_count)
            if is_feasible:
                feasible_set.add(candidate)
            if has_width:
                relevant.add(candidate)
            continue
        geometric = from_vertices(polytope.vertices, problem.objective_count) if good_geometry else None
        for a, b in pairs:
            if polytope.status == "infeasible" and not corrected:
                interval = infeasible_interval(polytope.message)
            elif geometric is not None:
                interval = geometric[a, b]
            else:
                interval = candidate_interval(problem, system, candidate, a, b)
            if ratios:
                intervals[a, b][candidate] = interval
            if feasible(interval):
                feasible_set.add(candidate)
            if positive_width(interval):
                relevant.add(candidate)
    selected = relevant if relevant else feasible_set
    candidates = tuple(candidate for candidate in checked if candidate in selected)
    # Normalize over *all checked candidates* before membership filtering.
    shares = None
    if volume_values is not None:
        total = float(sum(volume_values.values()))
        shares = {candidate: volume / total if total > 0 else 0.0
                  for candidate, volume in volume_values.items()}
    by_pair = (tuple(GoalPairRatioIntervals(a, b, FrozenMapping._from_owned(
                         {index: interval for index, interval in values.items() if index in selected}))
                     for (a, b), values in intervals.items()) if ratios else None)
    return CandidateAnalysis(candidates, by_pair,
                             None if volume_values is None else FrozenMapping._from_owned(
                                 {index: volume_values[index] for index in candidates}),
                             None if shares is None else FrozenMapping._from_owned(
                                 {index: shares[index] for index in candidates}))


def history_key(history):
    """Cache identity retains binary64 sign bits and original answer order."""
    return tuple((answer.query.goal_index_a, answer.query.goal_index_b,
                  struct.pack("!d", answer.query.value), answer.answer) for answer in history)


def interval_mapping(state):
    if state.analysis is None or state.analysis.ratio_intervals is None:
        return None
    return {(item.goal_index_a, item.goal_index_b): item for item in state.analysis.ratio_intervals}


def filtered_candidates(state, query, answer):
    subset = None if state.analysis is None else state.analysis.candidates
    mapping = interval_mapping(state)
    if subset is None or mapping is None or (query.goal_index_a, query.goal_index_b) not in mapping:
        return subset
    intervals = mapping[query.goal_index_a, query.goal_index_b].intervals_by_candidate
    return tuple(index for index in subset if index in intervals and
                 supports(intervals[index], query.value, answer, conservative=True))


class StateEngine:
    def __init__(self, problem, policy, geometry, session_id=None):
        self.problem, self.policy, self.geometry = problem, policy, geometry
        self.session_id = str(uuid4()) if session_id is None else str(session_id)
        self.cache = BoundedCache(16)

    def check(self, state):
        if (state.session_id != self.session_id or state.problem != self.problem
                or state.policy != self.policy):
            raise ValueError("prepared state belongs to another solver session")

    def bind(self, state):
        self.check(state)
        system = ConstraintSystem.from_key(state.weight_space.key, self.geometry.backend)
        system._geometry_owner = self.geometry
        return replace(state, weight_space=system.freeze())

    def _prepare(self, history, subset=None, *, terminal=False, need_volumes=False):
        key = history_key(history), subset, terminal, need_volumes
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        system = self.geometry.weight_space(history, self.problem.objective_count)
        is_feasible = system.is_feasible()
        analysis = candidate_analysis(self.problem, system, self.geometry, subset,
                                      ratios=not terminal, volumes=need_volumes) if is_feasible else None
        system.freeze()
        state = PreparedState(self.session_id, self.problem, self.policy, history, system,
                              is_feasible, analysis, subset)
        self.cache.put(key, state)
        return state

    def initial(self, history=(), *, need_volumes=False):
        return self._prepare(tuple(history), need_volumes=need_volumes)

    def advance(self, state, answered, *, terminal=False, need_volumes=False, probability=None,
                recovered=False, actual=False):
        self.check(state)
        subset = None if actual else filtered_candidates(state, answered.query, answered.answer)
        child = self._prepare(state.history + (answered,), subset, terminal=terminal, need_volumes=need_volumes)
        if child.is_feasible and subset == () and probability is not None and probability > 0 and recovered:
            try:
                winner, volume = recover_strict_singleton(
                    self.problem, state.weight_space, child.weight_space,
                    state.analysis.candidates, float(probability), answered.query, answered.answer)
            except (RecoveryNotApplicable, RecoveryGeometryError) as error:
                raise RuntimeError("recovered positive branch has no valid candidates") from error
            analysis = CandidateAnalysis((winner,), None,
                                         {winner: volume} if need_volumes else None,
                                         {winner: 1.0} if need_volumes else None)
            child = replace(child, is_feasible=True, analysis=analysis)
        return child

    def ensure_analysis(self, state, *, ratios=True, volumes=False):
        self.check(state)
        analysis = state.analysis
        if not state.is_feasible:
            return state
        if analysis is not None and (not ratios or analysis.ratio_intervals is not None) and (
                not volumes or analysis.candidate_volumes is not None):
            return state
        key = history_key(state.history), state.checked_candidates, not ratios, volumes
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        # Preserve the current candidate subset and its order. An existing
        # share analysis is not recomputed with a narrowed normalization set.
        computed = candidate_analysis(self.problem, state.weight_space, self.geometry,
                                      state.checked_candidates,
                                      ratios=ratios, volumes=volumes and (analysis is None or analysis.candidate_volumes is None))
        if analysis is not None and analysis.candidate_volumes is not None:
            computed = replace(computed, candidate_volumes=analysis.candidate_volumes,
                               candidate_volume_shares=analysis.candidate_volume_shares)
        prepared = replace(state, analysis=computed)
        self.cache.put(key, prepared)
        return prepared


def compute_terminal_candidate_count(state, query, answer, probability, *, recovered=False):
    """Original terminal interval shortcut; zero counts require full repair."""
    mapping = interval_mapping(state)
    if mapping is not None and (query.goal_index_a, query.goal_index_b) in mapping:
        count = sum(supports(interval, query.value, answer)
                    for interval in mapping[query.goal_index_a, query.goal_index_b].intervals_by_candidate.values())
        if count != 0 or probability <= 0:
            return int(count), bool(count > 0)
    # The backend belongs to the state engine's session. No additional session
    # or native pool is created for a terminal fallback.
    geometry = getattr(state.weight_space, "_geometry_owner", None)
    if geometry is None:
        raise ValueError("terminal fallback requires a session-bound state")
    child_space = geometry.weight_space(state.history + (AnsweredQuery(query, answer),), state.problem.objective_count)
    if not child_space.is_feasible():
        return 0, False
    analysis = candidate_analysis(state.problem, child_space, geometry,
                                  None if state.analysis is None else state.analysis.candidates,
                                  ratios=True, volumes=False)
    if not analysis.candidates and probability > 0 and recovered:
        subset = filtered_candidates(state, query, answer)
        if subset != ():
            raise RuntimeError("recovered positive branch has no valid candidates")
        try:
            recover_strict_singleton(state.problem, state.weight_space, child_space,
                                     state.analysis.candidates, probability, query, answer)
        except (RecoveryNotApplicable, RecoveryGeometryError) as error:
            raise RuntimeError("recovered positive branch has no valid candidates") from error
        return 1, True
    return len(analysis.candidates), True
