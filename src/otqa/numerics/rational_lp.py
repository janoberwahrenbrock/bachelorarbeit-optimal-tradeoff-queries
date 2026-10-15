"""Bounded complete rational recovery after an unclassified native LP failure."""
from fractions import Fraction
from itertools import combinations
import math

from .lp import LinearResult


def _dot(left, right):
    return sum((a * b for a, b in zip(left, right, strict=True)), Fraction(0))


def rref(matrix):
    rows = [list(row) for row in matrix]
    pivots = []
    position = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((index for index in range(position, len(rows)) if rows[index][column]), None)
        if pivot is None:
            continue
        rows[position], rows[pivot] = rows[pivot], rows[position]
        factor = rows[position][column]
        rows[position] = [value / factor for value in rows[position]]
        for index in range(len(rows)):
            if index != position:
                factor = rows[index][column]
                if factor:
                    rows[index] = [value - factor * pivot_value for value, pivot_value in
                                   zip(rows[index], rows[position], strict=True)]
        pivots.append(column)
        position += 1
        if position == len(rows):
            break
    return rows, pivots


def _basis(matrix, right, count):
    rows, _ = rref([list(row) + [rhs] for row, rhs in zip(matrix, right, strict=True)])
    if any(not any(row[:count]) and row[count] for row in rows):
        return (), (), True
    rows = [row for row in rows if any(row[:count])]
    return tuple(tuple(row[:count]) for row in rows), tuple(row[count] for row in rows), False


def _unique(matrix, right, count):
    rows, pivots = rref([list(row) + [rhs] for row, rhs in zip(matrix, right, strict=True)])
    if any(not any(row[:count]) and row[count] for row in rows):
        return None
    if len([column for column in pivots if column < count]) != count:
        return None
    point = [Fraction(0)] * count
    for row, column in zip(rows, pivots, strict=False):
        if column < count:
            point[column] = row[count]
    return tuple(point)


def _vertices(a, b, e, f, basis, basis_rhs, count):
    result = set()
    for active in combinations(range(len(a)), count - len(basis)):
        point = _unique(list(basis) + [a[index] for index in active],
                        list(basis_rhs) + [b[index] for index in active], count)
        if point is not None and (all(_dot(row, point) <= rhs for row, rhs in zip(a, b))
                                  and all(_dot(row, point) == rhs for row, rhs in zip(e, f))):
            result.add(point)
    return result


def recover_minimum(system, objective):
    count = len(objective)
    if not 1 <= count <= 5 or system.variable_count != count:
        return None
    def convert(value):
        return Fraction.from_float(float(value))
    try:
        c = tuple(map(convert, objective))
        a = tuple(tuple(map(convert, row)) for row in system.inequalities_left_side)
        b = tuple(map(convert, system.inequalities_right_side))
        e = tuple(tuple(map(convert, row)) for row in system.equalities_left_side)
        f = tuple(map(convert, system.equalities_right_side))
    except (ValueError, OverflowError):
        return None
    for column in range(count):
        if not any(rhs == 0 and row[column] < 0 and
                   all(value == 0 for index, value in enumerate(row) if index != column)
                   for row, rhs in zip(a, b)):
            return None
    basis, basis_rhs, inconsistent = _basis(e, f, count)
    if inconsistent:
        return LinearResult("infeasible", "min", solver_status_code=2,
                            solver_message="exact inconsistent equalities")
    ray_e = e + (tuple(Fraction(1) for _ in range(count)),)
    ray_f = tuple(Fraction(0) for _ in e) + (Fraction(1),)
    ray_basis, ray_rhs, ray_inconsistent = _basis(ray_e, ray_f, count)
    required = math.comb(len(a), count - len(basis))
    if not ray_inconsistent:
        required += math.comb(len(a), count - len(ray_basis))
    if required > 20_000:
        return None
    points = _vertices(a, b, e, f, basis, basis_rhs, count)
    if not points:
        return LinearResult("infeasible", "min", solver_status_code=2,
                            solver_message="exact complete active-set recovery")
    rays = set() if ray_inconsistent else _vertices(
        a, tuple(Fraction(0) for _ in b), ray_e, ray_f, ray_basis, ray_rhs, count)
    if any(_dot(c, ray) < 0 for ray in rays):
        return LinearResult("unbounded", "min", solver_status_code=3,
                            solver_message="exact improving recession ray")
    optimum = min((_dot(c, point), point) for point in points)[0]
    try:
        value = float(optimum)
    except OverflowError:
        return None
    if not math.isfinite(value) or (optimum != 0 and value == 0.0):
        return None
    return LinearResult("optimal", "min", value, 0, "exact complete active-set recovery")
