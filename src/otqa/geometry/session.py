"""Session-owned geometric work and reuse, without process-global caches."""
from __future__ import annotations

from functools import lru_cache

import numpy as np
from scipy.spatial import ConvexHull, QhullError

from otqa.numerics.cache import BoundedCache
from otqa.numerics.lp import LinearProgramBackend
from .affine import AffineCache
from .constraints import ConstraintSystem, optimality_region, weight_space
from .rational import RecoveryNotApplicable, RecoveryGeometryError, recover_volume, recover_probabilities
from .vertices import PolytopeVertices, enumerate_vertices


class _CorrectedVolume(float):
    exact_positive_correction = True


class _RecoveredZero(float):
    exact_exception_recovery = True


class GeometrySession:
    def __init__(self, numerical_profile=None, backend_factory=None):
        from otqa.numerics.profile import resolved_numerical_profile
        active_profile = resolved_numerical_profile()
        if numerical_profile is not None and numerical_profile != active_profile:
            raise ValueError("unrecognized or modified active numerical profile")
        self.numerical_profile = active_profile
        self.backend = (backend_factory or LinearProgramBackend)()
        self.affine = AffineCache()
        self.vertex_cache = BoundedCache(32768, 67_108_864, lambda key, value: value.vertices.nbytes)
        self.volume_cache = lru_cache(maxsize=32768)(self._compute_volume_by_key)
        self.support_hits = self.support_partial_hits = self.support_fallbacks = 0
        self.closed = False

    def _check_open(self):
        if self.closed:
            raise RuntimeError("geometry session is closed")

    def weight_space(self, history, goal_count):
        self._check_open()
        system = weight_space(goal_count, history, self.backend)
        system._geometry_owner = self
        return system

    def optimality_region(self, problem, system, index):
        self._check_open()
        if system.backend is not self.backend:
            system = ConstraintSystem.from_key(system.key, self.backend)
        return optimality_region(problem, system, index)

    def vertices(self, system, tolerance=1e-10):
        self._check_open()
        if system.backend is not self.backend:
            system = ConstraintSystem.from_key(system.key, self.backend)
        return enumerate_vertices(system, self.affine, tolerance)

    def _remember_vertices(self, key, tolerance, polytope):
        vertices = np.asarray(polytope.vertices, dtype=float)
        if (polytope.status != "full_dimensional" or vertices.ndim != 2 or len(vertices) == 0
                or not np.all(np.isfinite(vertices)) or vertices.nbytes > 67_108_864):
            return
        immutable = np.frombuffer(vertices.tobytes(), dtype=float).reshape(vertices.shape)
        cached = PolytopeVertices(polytope.status, immutable, polytope.affine_dimension,
                                  polytope.interior_radius, polytope.message)
        self.vertex_cache.put((key, float(tolerance)), cached)

    def volume_from_vertices(self, system, polytope):
        if polytope.status == "point":
            return 0.0
        if polytope.status in {"infeasible", "lower_dimensional"}:
            return self._recover_volume(system, zero=True)
        if polytope.status != "full_dimensional":
            error = RuntimeError(polytope.message or f"polytope status {polytope.status}")
            error.native_geometry_volume_error = True
            return self._recover_volume(system, error=error)
        _, _, e, f = system.get_solver_matrices()
        affine = self.affine.get(system.variable_count, e, f)
        coordinates = (np.asarray(polytope.vertices, dtype=float) - affine.particular_point) @ affine.basis
        dimension = coordinates.shape[1]
        if dimension == 0:
            return 0.0
        if dimension == 1:
            value = float(np.ptp(coordinates[:, 0]))
        else:
            try:
                value = float(ConvexHull(coordinates).volume)
            except QhullError:
                value = float(ConvexHull(coordinates, qhull_options="QJ").volume)
        return self._recover_volume(system, zero=True) if value == 0.0 else value

    def _recover_volume(self, system, *, zero=False, error=None):
        try:
            value = recover_volume(system)
            if value > 0.0:
                return _CorrectedVolume(value)
            return _RecoveredZero(0.0) if error is not None else 0.0
        except RecoveryNotApplicable:
            if zero:
                return 0.0
            raise error
        except RecoveryGeometryError as recovery_error:
            if error is None:
                error = RuntimeError("ambiguous zero intrinsic volume could not be certified")
                error.native_geometry_volume_error = True
            raise error from recovery_error

    def volume(self, system, tolerance=1e-10):
        self._check_open()
        if tolerance <= 0:
            raise ValueError("tolerance must be positive")
        return self._volume_by_key(system.key, tolerance)

    def _volume_by_key(self, constraint_key, tolerance=1e-10):
        """Do not materialize constraints on a volume-cache hit."""
        return self.volume_cache(constraint_key, float(tolerance))

    def _compute_volume_by_key(self, constraint_key, tolerance):
        system = ConstraintSystem.from_key(constraint_key, self.backend)
        polytope = self.vertices(system, tolerance)
        value = self.volume_from_vertices(system, polytope)
        if not getattr(value, "exact_positive_correction", False):
            self._remember_vertices(constraint_key, tolerance, polytope)
        return value

    def cached_support(self, system, objective, tolerance=1e-10, *, constraint_key=None):
        polytope = self.vertex_cache.get((system.key if constraint_key is None else constraint_key,
                                         float(tolerance)))
        if polytope is None:
            return None, None
        values = polytope.vertices @ np.asarray(objective, dtype=float)
        lower, upper = float(np.min(values)), float(np.max(values))
        coordinate_scale = max(1.0, float(np.max(np.abs(polytope.vertices))))
        objective_scale = max(1.0, float(np.sum(np.abs(objective))))
        margin = max(100.0 * tolerance, 1e-8) * coordinate_scale * objective_scale
        finite = np.isfinite(lower) and np.isfinite(upper)
        lower_uncertain, upper_uncertain = abs(lower) <= margin, abs(upper) <= margin
        if not finite or lower_uncertain or upper_uncertain:
            self.support_fallbacks += 1
            if finite and lower_uncertain != upper_uncertain:
                self.support_partial_hits += 1
                return None if lower_uncertain else lower, None if upper_uncertain else upper
            return None, None
        self.support_hits += 1
        return lower, upper

    def probabilities(self, system, query, tolerance=1e-10):
        self._check_open()
        if tolerance <= 0:
            raise ValueError("tolerance must be positive")
        if system.backend is not self.backend:
            system = ConstraintSystem.from_key(system.key, self.backend)
        objective = [0.0] * system.variable_count
        objective[query.goal_index_a], objective[query.goal_index_b] = 1.0, -query.value
        constraint_key = system.key
        lower, upper = self.cached_support(system, objective, tolerance, constraint_key=constraint_key)
        if lower is None:
            result = system.minimize(objective)
            if result.status != "optimal" or result.optimal_value is None:
                raise RuntimeError("cannot determine exact query support")
            lower = float(result.optimal_value)
        if upper is None:
            result = system.maximize(objective)
            if result.status != "optimal" or result.optimal_value is None:
                raise RuntimeError("cannot determine exact query support")
            upper = float(result.optimal_value)
        if lower >= -tolerance and upper <= tolerance:
            return {"<": 0.0, "=": 1.0, ">": 0.0}
        if lower >= -tolerance:
            return {"<": 0.0, "=": 0.0, ">": 1.0}
        if upper <= tolerance:
            return {"<": 1.0, "=": 0.0, ">": 0.0}
        try:
            total = self._volume_by_key(constraint_key, tolerance)
            if total <= 0:
                return recover_probabilities(system, query)
            inequalities, inequality_rhs, equalities, equality_rhs = constraint_key
            less_key = (inequalities + (tuple(objective),), inequality_rhs + (0.0,), equalities, equality_rhs)
            greater_key = (inequalities + (tuple(-value for value in objective),),
                           inequality_rhs + (0.0,), equalities, equality_rhs)
            left_volume = self._volume_by_key(less_key, tolerance)
            right_volume = self._volume_by_key(greater_key, tolerance)
        except RuntimeError as error:
            if not getattr(error, "native_geometry_volume_error", False):
                raise
            try:
                return recover_probabilities(system, query)
            except (RecoveryNotApplicable, RecoveryGeometryError) as recovery_error:
                raise error from recovery_error
        if any(getattr(value, "exact_positive_correction", False) or
               getattr(value, "exact_exception_recovery", False)
               for value in (total, left_volume, right_volume)):
            return recover_probabilities(system, query)
        raw = np.asarray([left_volume, right_volume], dtype=float) / total
        raw = np.maximum(raw, 0.0)
        probability_sum = float(np.sum(raw))
        if probability_sum <= 0:
            return recover_probabilities(system, query)
        raw /= probability_sum
        return {"<": float(raw[0]), "=": 0.0, ">": float(raw[1])}

    def close(self):
        if not self.closed:
            self.volume_cache.cache_clear()
            self.vertex_cache.clear()
            self.affine.cache.clear()
            self.backend.close()
            self.closed = True

    def __enter__(self):
        self._check_open()
        return self

    def __exit__(self, *exc):
        self.close()
