"""Candidate ratio bounds from complete geometry, with ordered LP fallbacks."""
from __future__ import annotations

import numpy as np

from otqa.geometry.constraints import optimality_region, ratio_normalized
from otqa.numerics.lp import LinearResult
from .types import RatioInterval


def ordered_pairs(goal_count):
    return [(a, b) for a in range(goal_count) for b in range(goal_count) if a != b]


def infeasible_interval(message=None):
    return RatioInterval(LinearResult("infeasible", "min", solver_message=message),
                         LinearResult("infeasible", "max", solver_message=message))


def ratio_bounds(system, numerator, denominator):
    normalized = ratio_normalized(system, denominator)
    objective = [0.0] * system.variable_count
    objective[numerator] = 1.0
    return RatioInterval(normalized.minimize(objective), normalized.maximize(objective))


def candidate_interval(problem, system, candidate, numerator, denominator):
    normalized = ratio_normalized(system, denominator)
    region = optimality_region(problem, normalized, candidate)
    objective = [0.0] * problem.objective_count
    objective[numerator] = 1.0
    return RatioInterval(region.minimize(objective), region.maximize(objective))


def from_vertices(vertices, goal_count, tolerance=1e-10):
    pairs = ordered_pairs(goal_count)
    ordinary = (type(vertices) is np.ndarray and vertices.ndim == 2
                and vertices.shape == (len(vertices), goal_count) and len(vertices) > 0
                and vertices.dtype == np.dtype(np.float64) and np.all(np.isfinite(vertices)))
    if not ordinary:
        return {(a, b): _one_interval(vertices, a, b, tolerance) for a, b in pairs}
    if len(vertices) > 4 * len(pairs) or len(vertices) * goal_count * goal_count > 1_048_576:
        return _prepared_pairs(vertices, goal_count, tolerance, pairs)
    positive = vertices > tolerance
    nonpositive = vertices <= tolerance
    has_positive = np.any(positive, axis=0)
    pair_mask = ~np.eye(goal_count, dtype=bool)
    ratio_mask = positive[:, None, :] & pair_mask[None, :, :]
    ratios = np.empty((len(vertices), goal_count, goal_count), dtype=np.float64)
    np.divide(vertices[:, :, None], vertices[:, None, :], out=ratios, where=ratio_mask)
    lowers = np.min(ratios, axis=0, where=ratio_mask, initial=np.inf)
    uppers = np.max(ratios, axis=0, where=ratio_mask, initial=-np.inf)
    unbounded = np.any(positive[:, :, None] & nonpositive[:, None, :], axis=0)
    result = {}
    for a, b in pairs:
        if not has_positive[b]:
            result[a, b] = infeasible_interval("ratio denominator is zero throughout candidate region")
        else:
            lower = LinearResult("optimal", "min", max(0.0, float(lowers[a, b])))
            upper = (LinearResult("unbounded", "max") if unbounded[a, b] else
                     LinearResult("optimal", "max", max(0.0, float(uppers[a, b]))))
            result[a, b] = RatioInterval(lower, upper)
    return result


def _prepared_pairs(vertices, goal_count, tolerance, pairs):
    columns = [vertices[:, index] for index in range(goal_count)]
    positive, nonpositive = vertices > tolerance, vertices <= tolerance
    has_positive = np.any(positive, axis=0)
    denominators = [column[positive[:, index]] for index, column in enumerate(columns)]
    result = {}
    for a, b in pairs:
        if not has_positive[b]:
            result[a, b] = infeasible_interval("ratio denominator is zero throughout candidate region")
            continue
        ratios = columns[a][positive[:, b]] / denominators[b]
        lower = LinearResult("optimal", "min", max(0.0, float(np.min(ratios))))
        upper = (LinearResult("unbounded", "max") if np.any(nonpositive[:, b] & positive[:, a]) else
                 LinearResult("optimal", "max", max(0.0, float(np.max(ratios)))))
        result[a, b] = RatioInterval(lower, upper)
    return result


def _one_interval(vertices, a, b, tolerance):
    numerator, denominator = vertices[:, a], vertices[:, b]
    positive = denominator > tolerance
    if not np.any(positive):
        return infeasible_interval("ratio denominator is zero throughout candidate region")
    ratios = numerator[positive] / denominator[positive]
    lower = LinearResult("optimal", "min", max(0.0, float(np.min(ratios))))
    upper = (LinearResult("unbounded", "max") if np.any((denominator <= tolerance) & (numerator > tolerance)) else
             LinearResult("optimal", "max", max(0.0, float(np.max(ratios)))))
    return RatioInterval(lower, upper)


def feasible(interval):
    return interval.lower.status == "optimal" and interval.upper.status in {"optimal", "unbounded"}


def lower_value(interval):
    if interval.lower.status == "unbounded":
        raise ValueError("lower ratio bound must not be unbounded")
    if interval.lower.status == "infeasible":
        return None
    if interval.lower.optimal_value is None:
        raise RuntimeError("optimal lower ratio bound has no value")
    return float(interval.lower.optimal_value)


def upper_value(interval):
    if interval.upper.status in {"unbounded", "infeasible"}:
        return None
    if interval.upper.optimal_value is None:
        raise RuntimeError("optimal upper ratio bound has no value")
    return float(interval.upper.optimal_value)


def positive_width(interval, tolerance=1e-12):
    if interval.lower.status != "optimal":
        return False
    if interval.upper.status == "unbounded":
        return True
    if interval.upper.status != "optimal":
        return False
    lower, upper = lower_value(interval), upper_value(interval)
    return lower is not None and upper is not None and upper > lower + tolerance


def supports(interval, value, answer, *, conservative=False, tolerance=1e-12):
    lower, upper = lower_value(interval), upper_value(interval)
    if lower is None:
        return False
    unbounded = interval.upper.status == "unbounded"
    if answer == "<":
        return lower < value + tolerance if conservative else lower < value - tolerance
    if answer == ">":
        return unbounded or (upper is not None and
                              (upper > value - tolerance if conservative else upper > value + tolerance))
    return lower <= value + tolerance and (unbounded or (upper is not None and upper >= value - tolerance))


def terminal_membership(vertices, goal_count, geometry_tolerance=1e-10, width_tolerance=1e-12):
    """Skip terminal interval objects while retaining the same reductions."""
    pairs = ordered_pairs(goal_count)
    if not (type(vertices) is np.ndarray and vertices.ndim == 2
            and vertices.shape == (len(vertices), goal_count) and len(vertices) > 0
            and vertices.dtype == np.dtype(np.float64) and np.all(np.isfinite(vertices))):
        intervals = from_vertices(vertices, goal_count, geometry_tolerance).values()
        return any(feasible(item) for item in intervals), any(positive_width(item, width_tolerance) for item in intervals)
    positive, nonpositive = vertices > geometry_tolerance, vertices <= geometry_tolerance
    has_positive = np.any(positive, axis=0)
    any_feasible = any(bool(has_positive[b]) for _, b in pairs)
    has_width = False
    if len(vertices) > 4 * len(pairs) or len(vertices) * goal_count * goal_count > 1_048_576:
        columns = [vertices[:, index] for index in range(goal_count)]
        denominators = [column[positive[:, index]] for index, column in enumerate(columns)]
        for a, b in pairs:
            if not has_positive[b]:
                continue
            ratios = columns[a][positive[:, b]] / denominators[b]
            lower = max(0.0, float(np.min(ratios)))
            if np.any(nonpositive[:, b] & positive[:, a]):
                has_width = True
            elif max(0.0, float(np.max(ratios))) > lower + width_tolerance:
                has_width = True
    else:
        ratio_mask = positive[:, None, :] & (~np.eye(goal_count, dtype=bool))[None, :, :]
        ratios = np.empty((len(vertices), goal_count, goal_count), dtype=np.float64)
        np.divide(vertices[:, :, None], vertices[:, None, :], out=ratios, where=ratio_mask)
        lowers = np.min(ratios, axis=0, where=ratio_mask, initial=np.inf)
        uppers = np.max(ratios, axis=0, where=ratio_mask, initial=-np.inf)
        unbounded = np.any(positive[:, :, None] & nonpositive[:, None, :], axis=0)
        for a, b in pairs:
            if has_positive[b] and (unbounded[a, b] or
                    max(0.0, float(uppers[a, b])) > max(0.0, float(lowers[a, b])) + width_tolerance):
                has_width = True
    return any_feasible, has_width
