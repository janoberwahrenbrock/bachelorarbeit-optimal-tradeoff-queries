"""Validated vertices in the affine hull of explicit equalities."""
from dataclasses import dataclass
from itertools import combinations

import numpy as np
from scipy.spatial import HalfspaceIntersection, QhullError

from otqa.numerics.lp import classify_failure


@dataclass(frozen=True)
class PolytopeVertices:
    status: str
    vertices: np.ndarray
    affine_dimension: int
    interior_radius: float | None = None
    message: str | None = None


def _empty(status, dimension, message, radius=None):
    return PolytopeVertices(status, np.empty((0, 0), dtype=float), dimension, radius, message)


def enumerate_vertices(system, affine_cache, tolerance=1e-10):
    if system.variable_count <= 0:
        return _empty("infeasible", 0, "system has no variables")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    a, b, e, f = system.get_solver_matrices()
    affine = affine_cache.get(system.variable_count, e, f)
    if affine.equality_residual > 10.0 * tolerance:
        return _empty("infeasible", 0, "inconsistent equalities")
    point, basis = affine.particular_point, affine.basis
    dimension = int(basis.shape[1])
    if a is None:
        return _empty("error", dimension, "bounded inequality system required")
    reduced, rhs = a @ basis, b - a @ point
    norms = np.linalg.norm(reduced, axis=1)
    constant = norms <= tolerance
    if np.any(rhs[constant] < -tolerance):
        return _empty("infeasible", dimension, "constant inequality violates affine hull")
    reduced, rhs, norms = reduced[~constant], rhs[~constant], norms[~constant]
    if dimension == 0:
        return PolytopeVertices("point", point.reshape(1, system.variable_count).copy(), 0, 0.0)
    if len(reduced) == 0:
        return _empty("error", dimension, "unbounded affine hull")
    backend = system.backend
    objective = np.concatenate((np.zeros(dimension), [-1.0]))
    bounds = [(None, None)] * dimension + [(0.0, None)]
    center_result = backend.solve(c=objective, A_ub=np.column_stack((reduced, norms)),
                                   b_ub=rhs, bounds=bounds)
    if not center_result.success or center_result.x is None:
        status = classify_failure(int(center_result.status), str(center_result.message))
        return _empty("infeasible" if status == "infeasible" else "error", dimension,
                      str(center_result.message))
    center, radius = np.asarray(center_result.x[:-1], dtype=float), float(center_result.x[-1])
    if not _valid_center(center, radius, reduced, rhs, norms, tolerance):
        center_result = backend.solve(
            c=objective,
            A_ub=np.column_stack((reduced / norms[:, None], np.ones(len(norms)))),
            b_ub=rhs / norms, bounds=bounds)
        if not center_result.success or center_result.x is None:
            return _empty("error", dimension, f"normalized center failed: {center_result.message}")
        center, radius = np.asarray(center_result.x[:-1], dtype=float), float(center_result.x[-1])
        if not _valid_center(center, radius, reduced, rhs, norms, tolerance):
            return _empty("error", dimension, "normalized center is invalid")
    radius = max(0.0, radius)
    if radius <= tolerance:
        return PolytopeVertices("lower_dimensional", np.empty((0, system.variable_count)),
                                dimension, radius, "inequalities reduce the explicit affine dimension")
    try:
        if dimension == 1:
            reduced_vertices = _interval(reduced, rhs, tolerance)
        else:
            reduced_vertices = _intersections(np.column_stack((reduced, -rhs)), center, dimension)
    except (QhullError, ValueError, RuntimeError) as error:
        return _empty("error", dimension, str(error), radius)
    if len(reduced_vertices) == 0:
        return _empty("error", dimension, "no enumerated vertices", radius)
    vertices = deduplicate_rows(point + reduced_vertices @ basis.T, tolerance)
    if not _valid_vertices(vertices, a, b, e, f, tolerance):
        return _empty("error", dimension, "enumerated vertices violate constraints", radius)
    return PolytopeVertices("full_dimensional", vertices, dimension, radius)


def _valid_center(center, radius, reduced, rhs, norms, tolerance):
    if not np.all(np.isfinite(center)) or not np.isfinite(radius) or radius < -tolerance:
        return False
    offsets = (reduced / norms[:, None]) @ center + (-rhs) / norms
    if not np.all(np.isfinite(offsets)):
        return False
    return bool(np.all(offsets < 0.0 if radius > tolerance else offsets <= tolerance))


def _intersections(halfspaces, center, dimension):
    coefficients, offsets = np.asarray(halfspaces[:, :-1], dtype=float), np.asarray(halfspaces[:, -1], dtype=float)
    norms = np.linalg.norm(coefficients, axis=1)
    if np.any(norms <= 0):
        raise ValueError("halfspace normals must be nonzero")
    normalized = coefficients / norms[:, None]
    center_offsets = normalized @ center + offsets / norms
    radius = float(np.min(-center_offsets, initial=np.inf))
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError("halfspace center is not strictly interior")
    conditioned = np.column_stack((normalized, center_offsets / radius))
    prefix = "Qx " if dimension > 4 else ""
    errors = []
    for options in (None, f"{prefix}Q12".strip(), f"{prefix}Q12 QJ".strip()):
        try:
            result = HalfspaceIntersection(conditioned, np.zeros_like(center), qhull_options=options)
            vertices = center + radius * np.asarray(result.intersections, dtype=float)
            if not _valid_halfspaces(vertices, halfspaces):
                vertices = _snap(vertices, halfspaces, dimension)
                if len(vertices) == 0 or not _valid_halfspaces(vertices, halfspaces):
                    errors.append(f"invalid intersections with {options!r}")
                    continue
            return vertices
        except (QhullError, ValueError, RuntimeError) as error:
            errors.append(str(error))
    raise RuntimeError("; ".join(errors))


def _valid_halfspaces(points, halfspaces):
    if points.ndim != 2 or halfspaces.ndim != 2 or len(points) == 0:
        return False
    if halfspaces.shape[1] != points.shape[1] + 1:
        return False
    a, b = halfspaces[:, :-1], halfspaces[:, -1]
    residual = a @ points.T + b[:, None]
    scales = np.maximum(1.0, np.linalg.norm(a, axis=1)[:, None] *
                        np.linalg.norm(points, axis=1)[None, :] + np.abs(b)[:, None])
    return not np.any(residual > 1e-8 * scales)


def _solve_snap(point, indices, coefficients, rhs, halfspaces):
    candidate, *_ = np.linalg.lstsq(coefficients[indices], rhs[indices], rcond=None)
    if not _valid_halfspaces(candidate.reshape(1, -1), halfspaces):
        return None
    scale = max(1.0, float(np.linalg.norm(point)), float(np.linalg.norm(candidate)))
    if float(np.linalg.norm(candidate - point)) > 1e-5 * scale:
        return None
    return np.asarray(candidate, dtype=float)


def _snap_one(point, coefficients, rhs, ordered, halfspaces, dimension):
    selected, rank = [], 0
    for index in map(int, ordered):
        trial = selected + [index]
        trial_rank = int(np.linalg.matrix_rank(coefficients[trial]))
        if trial_rank > rank:
            selected, rank = trial, trial_rank
        if rank == dimension:
            candidate = _solve_snap(point, selected, coefficients, rhs, halfspaces)
            if candidate is not None:
                return candidate
            break
    nearby = list(map(int, ordered[:min(len(ordered), dimension + 5)]))
    for active in combinations(nearby, dimension):
        if np.linalg.matrix_rank(coefficients[list(active)]) < dimension:
            continue
        candidate = _solve_snap(point, list(active), coefficients, rhs, halfspaces)
        if candidate is not None:
            return candidate
    return None


def _snap(points, halfspaces, dimension):
    coefficients = np.asarray(halfspaces[:, :-1], dtype=float)
    rhs = -np.asarray(halfspaces[:, -1], dtype=float)
    norms = np.linalg.norm(coefficients, axis=1)
    recovered = []
    for point in np.asarray(points, dtype=float):
        if _valid_halfspaces(point.reshape(1, -1), halfspaces):
            recovered.append(point)
            continue
        ordered = np.argsort(np.abs(coefficients @ point - rhs) / norms)
        candidate = _snap_one(point, coefficients, rhs, ordered, halfspaces, dimension)
        if candidate is None:
            return np.empty((0, dimension), dtype=float)
        recovered.append(candidate)
    return deduplicate_rows(np.asarray(recovered), 1e-10)


def _interval(matrix, rhs, tolerance):
    lower, upper = -np.inf, np.inf
    for coefficient, value in zip(matrix[:, 0], rhs):
        if coefficient > tolerance:
            upper = min(upper, float(value / coefficient))
        elif coefficient < -tolerance:
            lower = max(lower, float(value / coefficient))
        elif value < -tolerance:
            raise ValueError("infeasible constant inequality")
    if not np.isfinite(lower) or not np.isfinite(upper):
        raise ValueError("unbounded interval")
    if lower > upper + tolerance or abs(upper - lower) <= tolerance:
        raise ValueError("infeasible or lower-dimensional interval")
    return np.asarray([[lower], [upper]], dtype=float)


def deduplicate_rows(values, tolerance):
    rounded = np.round(values, decimals=max(0, int(-np.log10(tolerance))))
    if (type(values) is np.ndarray and values.ndim == 2 and values.shape[1] > 0
            and values.dtype == np.dtype(np.float64) and np.all(np.isfinite(rounded))):
        rounded[rounded == 0.0] = 0.0
        row_bytes = np.ascontiguousarray(rounded).view(
            np.dtype((np.void, rounded.dtype.itemsize * rounded.shape[1]))).reshape(-1)
        _, indices = np.unique(row_bytes, return_index=True)
    else:
        _, indices = np.unique(rounded, axis=0, return_index=True)
    return values[np.sort(indices)]


def _valid_vertices(vertices, a, b, e, f, tolerance):
    tolerance = max(1e-8, 100.0 * tolerance)
    norms = np.linalg.norm(vertices, axis=1)[None, :]
    scales = np.maximum(1.0, np.linalg.norm(a, axis=1)[:, None] * norms + np.abs(b)[:, None])
    if np.any(a @ vertices.T - b[:, None] > tolerance * scales):
        return False
    if e is not None and f is not None:
        scales = np.maximum(1.0, np.linalg.norm(e, axis=1)[:, None] * norms + np.abs(f)[:, None])
        if np.any(np.abs(e @ vertices.T - f[:, None]) > tolerance * scales):
            return False
    return True
