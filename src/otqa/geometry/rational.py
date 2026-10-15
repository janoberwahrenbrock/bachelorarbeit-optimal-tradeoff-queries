"""Exact binary-rational repairs for explicit affine dimension at most two.

These bounded repairs run only after the ordinary numerical method reaches
its specified ambiguous zero/error cases. Every constraint remains present.
"""
from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
import math


class RecoveryNotApplicable(ValueError):
    pass


class RecoveryGeometryError(RuntimeError):
    pass


def fraction(value):
    if not math.isfinite(float(value)):
        raise ValueError("finite coefficients required")
    return Fraction.from_float(float(value))


def eliminate(rows, rhs, count):
    matrix = [list(row) + [value] for row, value in zip(rows, rhs)]
    pivots, active = [], 0
    for column in range(count):
        pivot = next((index for index in range(active, len(matrix)) if matrix[index][column]), None)
        if pivot is None:
            continue
        matrix[active], matrix[pivot] = matrix[pivot], matrix[active]
        divisor = matrix[active][column]
        matrix[active] = [entry / divisor for entry in matrix[active]]
        for index in range(len(matrix)):
            if index != active and matrix[index][column]:
                multiplier = matrix[index][column]
                matrix[index] = [a - multiplier * b for a, b in zip(matrix[index], matrix[active])]
        pivots.append(column)
        active += 1
    if any(not any(row[:-1]) and row[-1] for row in matrix):
        raise RecoveryGeometryError("explicit equalities are exactly inconsistent")
    free = [column for column in range(count) if column not in pivots]
    constants = [Fraction(0)] * count
    basis = [[Fraction(0)] * len(free) for _ in range(count)]
    for index, column in enumerate(free):
        basis[column][index] = Fraction(1)
    for index, column in enumerate(pivots):
        constants[column] = matrix[index][-1]
        basis[column] = [-matrix[index][free_column] for free_column in free]
    return constants, basis, free


def reduce_row(row, rhs, constants, basis):
    reduced = [sum(a * coefficients[index] for a, coefficients in zip(row, basis))
               for index in range(len(basis[0]))]
    return reduced, rhs - sum(a * value for a, value in zip(row, constants))


def clip_polygon(polygon, coefficients, rhs):
    if not polygon:
        return []
    result, previous = [], polygon[-1]
    previous_value = sum(a * x for a, x in zip(coefficients, previous)) - rhs
    for current in polygon:
        current_value = sum(a * x for a, x in zip(coefficients, current)) - rhs
        if (previous_value <= 0) != (current_value <= 0):
            amount = previous_value / (previous_value - current_value)
            result.append(tuple(a + amount * (b - a) for a, b in zip(previous, current)))
        if current_value <= 0:
            result.append(current)
        previous, previous_value = current, current_value
    deduplicated = []
    for point in result:
        if not deduplicated or deduplicated[-1] != point:
            deduplicated.append(point)
    if len(deduplicated) > 1 and deduplicated[0] == deduplicated[-1]:
        deduplicated.pop()
    return deduplicated


def area(polygon):
    if len(polygon) < 3:
        return Fraction(0)
    return abs(sum(a[0] * b[1] - a[1] * b[0]
                   for a, b in zip(polygon, polygon[1:] + polygon[:1]))) / 2


def clip_interval(interval, coefficient, rhs):
    lower, upper = interval
    if coefficient > 0:
        upper = min(upper, rhs / coefficient)
    elif coefficient < 0:
        lower = max(lower, rhs / coefficient)
    elif rhs < 0:
        return Fraction(1), Fraction(0)
    return lower, upper


def intrinsic(measure, basis):
    if len(basis[0]) == 1:
        determinant = sum(row[0] ** 2 for row in basis)
    else:
        aa = sum(row[0] ** 2 for row in basis)
        ab = sum(row[0] * row[1] for row in basis)
        bb = sum(row[1] ** 2 for row in basis)
        determinant = aa * bb - ab * ab
    if determinant <= 0:
        raise RecoveryGeometryError("nonpositive affine metric determinant")
    with localcontext() as context:
        context.prec = 80
        projected = Decimal(measure.numerator) / Decimal(measure.denominator)
        squared = Decimal(determinant.numerator) / Decimal(determinant.denominator)
        return float(projected * squared.sqrt())


@dataclass(frozen=True)
class RationalRegion:
    constants: list
    basis: list
    free: list
    inequalities: list
    right: list
    region: object
    measure: Fraction

    @property
    def dimension(self):
        return len(self.free)


def region(system, *, volume_mode=False):
    count = system.variable_count
    if not count:
        raise RecoveryNotApplicable("system has no variables")
    if count > 3 and len(system.equalities_left_side) < count - 2:
        raise RecoveryNotApplicable("explicit equality rank leaves too many dimensions")
    a = [[fraction(value) for value in row] for row in system.inequalities_left_side]
    b = [fraction(value) for value in system.inequalities_right_side]
    e = [[fraction(value) for value in row] for row in system.equalities_left_side]
    f = [fraction(value) for value in system.equalities_right_side]
    simplex = any(row[0] and all(value == row[0] for value in row) and rhs == row[0]
                  for row, rhs in zip(e, f))
    nonnegative = all(any(row[column] < 0 and rhs <= 0 and
                         all(value == 0 for index, value in enumerate(row) if index != column)
                         for row, rhs in zip(a, b)) for column in range(count))
    if not simplex or not nonnegative:
        raise RecoveryNotApplicable("explicit simplex and nonnegative constraints required")
    constants, basis, free = eliminate(e, f, count)
    dimension = len(free)
    if dimension > 2:
        raise RecoveryNotApplicable("exact recovery supports explicit affine dimension at most two")
    if dimension == 0:
        if not volume_mode and any(sum(coefficient * value for coefficient, value in zip(row, constants)) > rhs
                                   for row, rhs in zip(a, b)):
            raise RecoveryGeometryError("equality-defined point violates an inequality")
        return RationalRegion(constants, basis, free, a, b, (), Fraction(0))
    reduced = [reduce_row(row, rhs, constants, basis) for row, rhs in zip(a, b)]
    if dimension == 1:
        current = Fraction(0), Fraction(1)
        for row, rhs in reduced:
            current = clip_interval(current, row[0], rhs)
        measure = max(Fraction(0), current[1] - current[0])
    else:
        current = [(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)),
                   (Fraction(1), Fraction(1)), (Fraction(0), Fraction(1))]
        for row, rhs in reduced:
            current = clip_polygon(current, row, rhs)
        measure = area(current)
    return RationalRegion(constants, basis, free, a, b, current, measure)


def recover_volume(system):
    try:
        exact = region(system, volume_mode=True)
    except RecoveryGeometryError as error:
        if str(error) == "explicit equalities are exactly inconsistent":
            return 0.0
        raise
    if exact.dimension == 0 or exact.measure == 0:
        return 0.0
    value = intrinsic(exact.measure, exact.basis)
    if not math.isfinite(value) or value <= 0:
        raise RecoveryGeometryError("positive intrinsic volume is outside finite positive binary64")
    return value


def partition(system, query):
    exact = region(system)
    objective = [Fraction(0)] * system.variable_count
    objective[query.goal_index_a], objective[query.goal_index_b] = Fraction(1), -fraction(query.value)
    if exact.dimension == 0:
        value = sum(a * weight for a, weight in zip(objective, exact.constants))
        answer = "<" if value < 0 else ">" if value > 0 else "="
        probabilities = {option: Fraction(option == answer) for option in ("<", "=", ">")}
        return probabilities, exact
    cut, rhs = reduce_row(objective, Fraction(0), exact.constants, exact.basis)
    if exact.measure <= 0:
        raise RecoveryGeometryError("parent has exactly zero explicit affine measure")
    if not any(cut) and rhs == 0:
        probabilities = {"<": Fraction(0), "=": Fraction(1), ">": Fraction(0)}
    else:
        if exact.dimension == 1:
            left = clip_interval(exact.region, cut[0], rhs)
            right = clip_interval(exact.region, -cut[0], -rhs)
            less = max(Fraction(0), left[1] - left[0])
            greater = max(Fraction(0), right[1] - right[0])
        else:
            less = area(clip_polygon(exact.region, cut, rhs))
            greater = area(clip_polygon(exact.region, [-value for value in cut], -rhs))
        if less + greater != exact.measure:
            raise RecoveryGeometryError("child measures do not exactly partition parent")
        probabilities = {"<": less / exact.measure, "=": Fraction(0), ">": greater / exact.measure}
    return probabilities, exact


class RecoveredProbabilities(dict):
    recovered_exact_partition = True


def recover_probabilities(system, query):
    probabilities, _ = partition(system, query)
    converted = {answer: float(value) for answer, value in probabilities.items()}
    if any(value > 0 and converted[answer] == 0 for answer, value in probabilities.items()):
        raise RecoveryGeometryError("positive probability underflows binary64")
    return RecoveredProbabilities(converted)


def recover_strict_singleton(problem, parent, child, candidates, probability, query, answer):
    if not math.isfinite(probability) or not 0 < probability <= 1 or not candidates:
        raise RecoveryNotApplicable("positive branch and nonempty parent subset required")
    exact_probability, parent_region = partition(parent, query)
    if parent_region.dimension not in (1, 2) or exact_probability[answer] <= 0:
        raise RecoveryNotApplicable("positive one/two-dimensional parent required")
    exact = region(child)
    if exact.dimension not in (1, 2) or exact.measure <= 0:
        raise RecoveryNotApplicable("positive one/two-dimensional child required")
    feasible = []
    for candidate in candidates:
        current = list(exact.region) if exact.dimension == 2 else exact.region
        for other, row in enumerate(problem.alternatives):
            if other != candidate:
                difference = [fraction(float(a) - float(b))
                              for a, b in zip(row, problem.alternatives[candidate])]
                coefficients, rhs = reduce_row(difference, Fraction(0), exact.constants, exact.basis)
                current = clip_polygon(current, coefficients, rhs) if exact.dimension == 2 else clip_interval(current, coefficients[0], rhs)
        closed = bool(current) if exact.dimension == 2 else current[0] <= current[1]
        measure = area(current) if exact.dimension == 2 else max(Fraction(0), current[1] - current[0])
        if closed:
            feasible.append((candidate, measure))
    if len(feasible) != 1 or feasible[0][1] != exact.measure:
        raise RecoveryNotApplicable("unique complete child winning region unproved")
    winner = feasible[0][0]
    coordinates = exact.region if exact.dimension == 2 else [(value,) for value in exact.region]
    minimum = None
    for coordinate in coordinates:
        weights = [constant + sum(a * value for a, value in zip(row, coordinate))
                   for constant, row in zip(exact.constants, exact.basis)]
        utility = sum(fraction(value) * weight for value, weight in zip(problem.alternatives[winner], weights))
        for other, row in enumerate(problem.alternatives):
            if other != winner:
                margin = utility - sum(fraction(value) * weight for value, weight in zip(row, weights))
                minimum = margin if minimum is None else min(minimum, margin)
    if minimum is None or minimum <= 0:
        raise RecoveryNotApplicable("strict global dominance is unproved")
    volume = intrinsic(exact.measure, exact.basis)
    if volume <= 0:
        raise RecoveryGeometryError("positive child volume underflows binary64")
    return winner, volume
