"""Deterministically ordered ratio/grid queries and their source provenance."""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from otqa.models import Query
from otqa.state.ratios import ordered_pairs, ratio_bounds


def query_key(query):
    return query.goal_index_a, query.goal_index_b, float(query.value)


def canonical_key(query):
    direct = query_key(query)
    return direct if query.value <= 0 else min(direct, (query.goal_index_b, query.goal_index_a, 1.0 / query.value))


def _same(left, right, abs_tol=1e-12, rel_tol=1e-9):
    return left[:2] == right[:2] and math.isclose(left[2], right[2], abs_tol=abs_tol, rel_tol=rel_tol)


def deduplicate_mirrors(queries, *, capture_filter=None):
    if capture_filter is None:
        pairs = [(query, canonical_key(query)) for query in queries if query.value > 0]
    else:
        pairs = []
        for query in queries:
            retained = query.value > 0
            capture_filter("nonpositive_value", query, retained)
            if retained:
                pairs.append((query, canonical_key(query)))
    pairs.sort(key=lambda item: item[1])
    result, previous = [], None
    for query, key in pairs:
        retained = previous is None or not _same(previous, key)
        if capture_filter is not None:
            capture_filter("mirror_duplicate", query, retained)
        if retained:
            result.append(query)
            previous = key
    return sorted(result, key=query_key)


@dataclass(frozen=True)
class _Breakpoint:
    a: int
    b: int
    side: str
    value: float

    @property
    def key(self):
        return self.a, self.b, self.side, self.value

    def query_value(self, epsilon):
        return self.value - epsilon if self.side == "left" else self.value + epsilon

    def mirror(self):
        return _Breakpoint(self.b, self.a, "right" if self.side == "left" else "left", 1.0 / self.value)


def _deduplicate_breakpoints(points, *, abs_tol, rel_tol):
    result = []
    for point in points:
        if not result or not (result[-1].key[:3] == point.key[:3] and
                              math.isclose(result[-1].value, point.value, abs_tol=abs_tol, rel_tol=rel_tol)):
            result.append(point)
    return result


def _canonical_breakpoint(point, epsilon):
    if point.value <= 0:
        return point
    mirror = point.mirror()
    direct_value, mirror_value = point.query_value(epsilon), mirror.query_value(epsilon)
    if mirror_value < 0:
        return point
    if direct_value < 0:
        return mirror
    if direct_value >= 1 and mirror_value < 1:
        return point
    if mirror_value >= 1 and direct_value < 1:
        return mirror
    if math.isclose(direct_value, mirror_value, abs_tol=1e-12, rel_tol=1e-9):
        return min(point, mirror, key=lambda item: item.key)
    return max(point, mirror, key=lambda item: item.query_value(epsilon))


def ratio_queries(goal_pair_intervals, epsilon=1e-3, *, capture_filter=None):
    raw = []
    for pair in goal_pair_intervals:
        points = []
        for interval in pair.intervals_by_candidate.values():
            lower, upper = interval.lower, interval.upper
            if lower.status == "unbounded":
                raise ValueError("lower ratio bound must not be unbounded")
            if lower.status == "optimal":
                if lower.optimal_value is None:
                    raise RuntimeError("optimal lower ratio bound has no value")
                if lower.optimal_value > epsilon:
                    points.append(_Breakpoint(pair.goal_index_a, pair.goal_index_b, "left", float(lower.optimal_value)))
            if upper.status == "optimal":
                if upper.optimal_value is None:
                    raise RuntimeError("optimal upper ratio bound has no value")
                points.append(_Breakpoint(pair.goal_index_a, pair.goal_index_b, "right", float(upper.optimal_value)))
        points.sort(key=lambda item: (item.side, item.value))
        raw.extend(_deduplicate_breakpoints(points, abs_tol=1e-12, rel_tol=0.0))
    canonical = sorted((_canonical_breakpoint(point, epsilon) for point in raw), key=lambda item: item.key)
    canonical = _deduplicate_breakpoints(canonical, abs_tol=1e-12, rel_tol=1e-9)
    queries = []
    for point in canonical:
        value = point.query_value(epsilon)
        if value < 0 and math.isclose(value, 0.0, abs_tol=1e-12, rel_tol=0.0):
            value = 0.0
        queries.append(Query(point.a, point.b, value))
    queries.sort(key=query_key)
    deduplicated = []
    for query in queries:
        retained = not deduplicated or not _same(query_key(deduplicated[-1]), query_key(query))
        if capture_filter is not None:
            capture_filter("ratio_duplicate", query, retained)
        if retained:
            deduplicated.append(query)
    return tuple(deduplicated)


def grid_values(interval, grid_size, *, minimum=1e-3, maximum=100.0):
    lower, upper = interval.lower, interval.upper
    if lower.status == "unbounded":
        raise ValueError("lower ratio bound must not be unbounded")
    if lower.status != "optimal" or upper.status == "infeasible":
        return []
    if lower.optimal_value is None or (upper.status == "optimal" and upper.optimal_value is None):
        raise RuntimeError("optimal ratio bound has no value")
    start = max(float(lower.optimal_value), minimum)
    stop = maximum if upper.status == "unbounded" else min(float(upper.optimal_value), maximum)
    if stop < minimum or start > stop:
        return []
    if math.isclose(start, stop, abs_tol=1e-15, rel_tol=1e-12):
        return [start]
    return np.geomspace(start, stop, grid_size, dtype=float).tolist()


def grid_queries(system, grid_size, *, capture_filter=None):
    queries = []
    for a, b in ordered_pairs(system.variable_count):
        interval = ratio_bounds(system, a, b)
        queries.extend(Query(a, b, value) for value in grid_values(interval, grid_size))
    return tuple(deduplicate_mirrors(queries, capture_filter=capture_filter))


def already_answered(query, history):
    for answered in history:
        previous = answered.query
        if _same(query_key(query), query_key(previous)):
            return True
        if query.value > 0 and previous.value > 0 and _same(
                query_key(query), (previous.goal_index_b, previous.goal_index_a, 1.0 / previous.value)):
            return True
    return False


@dataclass(frozen=True)
class QueryCandidateData:
    query_candidates: tuple[Query, ...]
    query_sources: dict[tuple[int, int, float], str]
    ratio_intervals_by_goal_pair: dict | None


def generate_queries(state, depth, *, capture_filter=None):
    if depth <= 0:
        return QueryCandidateData((), {}, None)
    analysis = state.analysis
    intervals = None if analysis is None else analysis.ratio_intervals
    if intervals is None:
        raise ValueError("query generation requires prepared ratio analyses")
    policy = state.policy
    mode = policy.higher_depth_query_source
    grid = grid_queries(state.weight_space, policy.grid_size, capture_filter=capture_filter) if depth > 1 else ()
    ratio = ratio_queries(intervals, capture_filter=capture_filter) if depth == 1 or mode == "both" else ()
    sources = {}
    for label, queries in (("grid", grid), ("ratio", ratio)):
        for query in queries:
            sources.setdefault(canonical_key(query), set()).add(label)
            if capture_filter is not None:
                capture_filter("source_" + label, query, True)
    merged = deduplicate_mirrors(list(grid) + list(ratio), capture_filter=capture_filter)
    if capture_filter is None:
        merged = tuple(query for query in merged if not already_answered(query, state.history))
    else:
        retained_queries = []
        for query in merged:
            retained = not already_answered(query, state.history)
            capture_filter("already_answered", query, retained)
            if retained:
                retained_queries.append(query)
        merged = tuple(retained_queries)
    source_mapping = {canonical_key(query): "+".join(label for label in ("grid", "ratio")
                                                     if label in sources.get(canonical_key(query), ())) or "unknown"
                      for query in merged}
    interval_mapping = {(item.goal_index_a, item.goal_index_b): item for item in intervals}
    return QueryCandidateData(merged, source_mapping, interval_mapping)
