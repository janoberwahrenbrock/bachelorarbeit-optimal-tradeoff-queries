"""Ordered linear constraints and their immutable numerical signatures."""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import TYPE_CHECKING

import numpy as np

from otqa.numerics.lp import LinearProgramBackend, LinearResult, classify_failure

if TYPE_CHECKING:
    from otqa.models import AnsweredQuery, Problem


@dataclass
class ConstraintSystem:
    inequalities_left_side: list[list[float]] = field(default_factory=list)
    inequalities_right_side: list[float] = field(default_factory=list)
    equalities_left_side: list[list[float]] = field(default_factory=list)
    equalities_right_side: list[float] = field(default_factory=list)
    backend: LinearProgramBackend | None = field(default=None, repr=False, compare=False)
    _matrices: tuple | None = field(default=None, init=False, repr=False, compare=False)
    _frozen: bool = field(default=False, init=False, repr=False, compare=False)
    _frozen_key: tuple | None = field(default=None, init=False, repr=False, compare=False)

    def __setattr__(self, name, value):
        if self.__dict__.get("_frozen", False) and name in {
            "inequalities_left_side", "inequalities_right_side", "equalities_left_side",
            "equalities_right_side", "_matrices", "_frozen", "_frozen_key",
        }:
            raise AttributeError("prepared mathematical constraints are immutable")
        object.__setattr__(self, name, value)

    def __post_init__(self):
        n = self.variable_count
        for rows, rhs in ((self.inequalities_left_side, self.inequalities_right_side),
                          (self.equalities_left_side, self.equalities_right_side)):
            if len(rows) != len(rhs) or any(len(row) != n for row in rows):
                raise ValueError("constraint dimensions differ")
            if any(not math.isfinite(float(value)) for row in rows for value in row):
                raise ValueError("constraint coefficients must be finite")
            if any(not math.isfinite(float(value)) for value in rhs):
                raise ValueError("constraint right sides must be finite")

    @property
    def variable_count(self):
        rows = self.equalities_left_side or self.inequalities_left_side
        return len(rows[0]) if rows else 0

    @property
    def key(self):
        if self._frozen_key is not None:
            return self._frozen_key
        return (tuple(tuple(float(value) for value in row) for row in self.inequalities_left_side),
                tuple(float(value) for value in self.inequalities_right_side),
                tuple(tuple(float(value) for value in row) for row in self.equalities_left_side),
                tuple(float(value) for value in self.equalities_right_side))

    @classmethod
    def from_key(cls, key, backend=None):
        a, b, e, f = key
        return cls([list(row) for row in a], list(b), [list(row) for row in e], list(f), backend)

    def copy(self):
        return type(self).from_key(self.key, self.backend)

    def __getstate__(self):
        # Prepared root transfers contain mathematical values, never native
        # models, session caches, locks, or backend handles.
        return self.key, self._frozen

    def __setstate__(self, state):
        key, frozen = state
        restored = type(self).from_key(key)
        if frozen:
            restored.freeze()
        self.__dict__.update(restored.__dict__)

    def freeze(self):
        """Freeze prepared inputs once; copies remain mutable builders."""
        if self._frozen:
            return self
        key = self.key
        self.inequalities_left_side, self.inequalities_right_side = key[:2]
        self.equalities_left_side, self.equalities_right_side = key[2:]
        arrays = self.get_solver_matrices()
        # Existing matrices are contiguous float64. Bytes-backed storage makes
        # setflags(write=True) impossible and preserves every binary64 value.
        self._matrices = tuple(None if array is None else
                               np.frombuffer(array.tobytes(), dtype=array.dtype).reshape(array.shape)
                               for array in arrays)
        self._frozen_key = key
        self._frozen = True
        return self

    def _add(self, row, rhs, equality):
        if self._frozen:
            raise AttributeError("prepared mathematical constraints are immutable")
        if not row or (self.variable_count and len(row) != self.variable_count):
            raise ValueError("constraint row has invalid dimension")
        if not all(math.isfinite(float(value)) for value in (*row, rhs)):
            raise ValueError("constraint must be finite")
        rows = self.equalities_left_side if equality else self.inequalities_left_side
        right = self.equalities_right_side if equality else self.inequalities_right_side
        rows.append(list(row))
        right.append(rhs)
        self._matrices = None

    def add_inequality(self, row, rhs):
        self._add(row, rhs, False)

    def add_equality(self, row, rhs):
        self._add(row, rhs, True)

    def get_solver_matrices(self):
        if self._matrices is None:
            self._matrices = tuple(np.asarray(values, dtype=float) if values else None for values in (
                self.inequalities_left_side, self.inequalities_right_side,
                self.equalities_left_side, self.equalities_right_side))
        return self._matrices

    def _solve(self, objective):
        if len(objective) != self.variable_count:
            raise ValueError("objective dimension differs from constraints")
        a, b, e, f = self.get_solver_matrices()
        if self.backend is None:
            self.backend = LinearProgramBackend()
        return self.backend.solve(c=objective, A_ub=a, b_ub=b, A_eq=e, b_eq=f,
                                  bounds=[(None, None)] * self.variable_count)

    def minimize(self, objective):
        if self.variable_count <= 0:
            return LinearResult("infeasible", "min", solver_message="system has no variables")
        result = self._solve(objective)
        if result.success:
            if result.x is None or result.fun is None:
                raise RuntimeError("LP success without primal solution")
            return LinearResult("optimal", "min", float(result.fun), int(result.status), str(result.message))
        failure = classify_failure(int(result.status), str(result.message))
        if failure is not None:
            return LinearResult(failure, "min", solver_status_code=int(result.status),
                                solver_message=str(result.message))
        from otqa.numerics.rational_lp import recover_minimum
        recovered = recover_minimum(self, objective)
        if recovered is not None:
            return recovered
        raise RuntimeError(f"linprog failed: {result.message}")

    def maximize(self, objective):
        result = self.minimize([-value for value in objective])
        return LinearResult(result.status, "max",
                            -result.optimal_value if result.optimal_value is not None else None,
                            result.solver_status_code, result.solver_message)

    def is_feasible(self):
        return self.variable_count > 0 and self.minimize([0.0] * self.variable_count).status == "optimal"

    def find_feasible_point(self):
        result = self._solve([0.0] * self.variable_count)
        if result.success and result.x is not None:
            return result.x.astype(float).tolist()
        failure = classify_failure(int(result.status), str(result.message))
        if failure is not None:
            raise ValueError(f"system is {failure}")
        raise RuntimeError(f"linprog failed: {result.message}")


def answered_constraint(answered: AnsweredQuery, goal_count: int):
    query, answer = answered.query, answered.answer
    if max(query.goal_index_a, query.goal_index_b) >= goal_count:
        raise IndexError("query goal index out of range")
    row = [0.0] * goal_count
    row[query.goal_index_a] = -1.0 if answer == ">" else 1.0
    row[query.goal_index_b] = query.value if answer == ">" else -query.value
    scale = max(abs(value) for value in row)
    return [value / scale for value in row], 0.0, answer == "="


def weight_space(goal_count: int, history=(), backend=None):
    system = ConstraintSystem(backend=backend)
    for index in range(goal_count):
        row = [0.0] * goal_count
        row[index] = -1.0
        system.add_inequality(row, 0.0)
    system.add_equality([1.0] * goal_count, 1.0)
    for answered in history:
        row, rhs, equality = answered_constraint(answered, goal_count)
        (system.add_equality if equality else system.add_inequality)(row, rhs)
    return system


def ratio_normalized(system: ConstraintSystem, denominator: int, tolerance=1e-12):
    normalized = ConstraintSystem(backend=system.backend)
    for row, rhs in zip(system.inequalities_left_side, system.inequalities_right_side):
        if abs(rhs) > tolerance:
            raise ValueError("ratio normalization requires homogeneous inequalities")
        normalized.add_inequality(row, rhs)
    for row, rhs in zip(system.equalities_left_side, system.equalities_right_side):
        if abs(rhs - 1.0) <= tolerance and all(abs(value - 1.0) <= tolerance for value in row):
            continue
        if abs(rhs) > tolerance:
            raise ValueError("ratio normalization requires homogeneous equalities")
        normalized.add_equality(row, rhs)
    row = [0.0] * system.variable_count
    row[denominator] = 1.0
    normalized.add_equality(row, 1.0)
    return normalized


def optimality_region(problem: Problem, system: ConstraintSystem, index: int):
    if not 0 <= index < problem.alternative_count:
        raise IndexError("alternative index out of range")
    region = system.copy()
    for other_index, other in enumerate(problem.alternatives):
        if other_index != index:
            region.add_inequality([float(a) - float(b) for a, b in
                                   zip(other, problem.alternatives[index])], 0.0)
    return region
