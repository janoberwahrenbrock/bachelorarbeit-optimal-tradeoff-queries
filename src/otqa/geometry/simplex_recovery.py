"""Bounded exact partition recovery on an explicitly constrained weight simplex.

Incremental rational H-to-V clips and recursive pulling triangulation support
only ambient dimension n-1<=6, with all original source constraints retained.
Unsupported domains are separate from failed bounded recovery. This module has
no native geometry, LP, file, thread, oracle, application or run dependencies.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields, replace
from fractions import Fraction
import math
import time

from otqa.numerics.profile import resolved_numerical_profile
from .rational import RecoveredProbabilities, RecoveryGeometryError, RecoveryNotApplicable


class ExactPartitionError(RuntimeError):
    """No numerical answer may be substituted for this typed failure."""

    code = "exact_partition_error"


class UnsupportedGeometry(ExactPartitionError):
    code = "unsupported_geometry"


class WorkLimitExceeded(ExactPartitionError):
    code = "work_limit_exceeded"


class ExactInvariantError(ExactPartitionError):
    code = "exact_invariant_error"


class ZeroParentVolume(ExactPartitionError):
    code = "zero_parent_volume"


class ProbabilityUnderflow(ExactPartitionError):
    code = "positive_probability_float_underflow"


@dataclass(frozen=True)
class Limits:
    max_goals: int = 7
    max_constraints: int = 96
    max_vertices: int = 1024
    max_pair_checks: int = 200_000
    max_rank_calls: int = 100_000
    max_faces: int = 30_000
    max_simplices: int = 100_000
    max_operations: int = 3_000_000
    max_bits: int = 8192
    max_wall_seconds: float = 45.0


@dataclass
class Budget:
    limits: Limits = field(default_factory=Limits)
    started: float = field(default_factory=time.perf_counter)
    counts: dict = field(default_factory=dict)
    peak_vertices: int = 0
    max_fraction_bits: int = 0

    def __post_init__(self):
        for name, value in asdict(self.limits).items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0 or not math.isfinite(value):
                raise UnsupportedGeometry(f"Invalid positive limit {name}")

    def tick(self, name="operations", amount=1):
        self.counts[name] = self.counts.get(name, 0) + amount
        limit = getattr(self.limits, "max_" + name, None)
        if limit is not None and self.counts[name] > limit:
            self.exhausted(f"{name} limit exceeded: {self.counts[name]} > {limit}")
        if time.perf_counter() - self.started > self.limits.max_wall_seconds:
            self.exhausted("Shared exact-recovery wall budget exceeded")

    def exhausted(self, message):
        error = WorkLimitExceeded(message)
        error.budget = self.report()
        raise error

    def checked(self, value):
        size = max(abs(value.numerator).bit_length(), value.denominator.bit_length())
        self.max_fraction_bits = max(size, self.max_fraction_bits)
        if size > self.limits.max_bits:
            self.exhausted(f"Fraction bit bound exceeded: {size}")
        return value

    def add(self, a, b):
        self.tick()
        return self.checked(a + b)

    def sub(self, a, b):
        self.tick()
        return self.checked(a - b)

    def mul(self, a, b):
        self.tick()
        return self.checked(a * b)

    def div(self, a, b):
        self.tick()
        if not b:
            raise ExactInvariantError("Unexpected exact zero divisor")
        return self.checked(a / b)

    def vertices(self, count):
        self.peak_vertices = max(count, self.peak_vertices)
        if count > self.limits.max_vertices:
            self.exhausted(f"Vertex bound exceeded: {count}")
        self.tick()

    def report(self):
        return {"limits": asdict(self.limits), "counts": dict(self.counts),
                "peak_vertices": self.peak_vertices, "max_fraction_bits": self.max_fraction_bits,
                "wall_seconds": time.perf_counter() - self.started}


def rational(value, budget):
    budget.tick()
    if isinstance(value, bool):
        raise UnsupportedGeometry("Boolean coefficient")
    if isinstance(value, Fraction):
        result = value
    elif isinstance(value, int):
        result = Fraction(value)
    elif isinstance(value, float) and math.isfinite(value):
        result = Fraction.from_float(value)
    else:
        raise UnsupportedGeometry("Coefficients must be finite Binary64, int or Fraction")
    return budget.checked(result)


def dot(a, b, budget):
    result = Fraction(0)
    for x, y in zip(a, b):
        result = budget.add(result, budget.mul(x, y))
    return result


def rank(rows, budget):
    budget.tick("rank_calls")
    a = [list(row) for row in rows]
    if not a:
        return 0
    columns = len(a[0])
    if any(len(row) != columns for row in a):
        raise ExactInvariantError("Ragged exact rank matrix")
    pivot = 0
    for col in range(columns):
        found = next((i for i in range(pivot, len(a)) if a[i][col]), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        value = a[pivot][col]
        for i in range(pivot + 1, len(a)):
            if not a[i][col]:
                continue
            scale = budget.div(a[i][col], value)
            for j in range(col + 1, columns):
                a[i][j] = budget.sub(a[i][j], budget.mul(scale, a[pivot][j]))
            a[i][col] = Fraction(0)
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def determinant(rows, budget):
    a = [list(row) for row in rows]
    n = len(a)
    if any(len(row) != n for row in a):
        raise ExactInvariantError("Nonsquare determinant")
    result = Fraction(1)
    for col in range(n):
        found = next((i for i in range(col, n) if a[i][col]), None)
        if found is None:
            return Fraction(0)
        if found != col:
            a[col], a[found] = a[found], a[col]
            result = -result
        value = a[col][col]
        result = budget.mul(result, value)
        for i in range(col + 1, n):
            if not a[i][col]:
                continue
            scale = budget.div(a[i][col], value)
            for j in range(col + 1, n):
                a[i][j] = budget.sub(a[i][j], budget.mul(scale, a[col][j]))
            a[i][col] = Fraction(0)
    return result


@dataclass(frozen=True)
class Halfspace:
    a: tuple
    b: Fraction


def canonical_row(a, b, budget):
    """Positive scaling only; exact duplicates/redundant multiples share a row."""
    first = next((abs(x) for x in (*a, b) if x), None)
    if first is None:
        return Halfspace(tuple(a), b)
    return Halfspace(tuple(budget.div(x, first) for x in a), budget.div(b, first))


def reduced_row(n, row, budget):
    try:
        a, b = row
    except (TypeError, ValueError) as error:
        raise UnsupportedGeometry("A halfspace must be (normal, rhs)") from error
    if len(a) != n:
        raise UnsupportedGeometry("Halfspace dimension differs from simplex")
    a = tuple(rational(x, budget) for x in a)
    b = rational(b, budget)
    # Eliminate precisely the same last weight in every parent/child region.
    return canonical_row(tuple(budget.sub(x, a[-1]) for x in a[:-1]),
                         budget.sub(b, a[-1]), budget)


@dataclass(frozen=True)
class Polytope:
    n: int
    vertices: tuple
    rows: tuple
    status: str = "full_dimensional"
    dimension_upper_bound: int | None = None
    unprocessed_constraints: int = 0

    @property
    def d(self):
        return self.n - 1


def slack(row, vertex, budget):
    return budget.sub(row.b, dot(row.a, vertex, budget))


def checked_vertices(vertices, rows, budget):
    for vertex in vertices:
        for row in rows:
            if slack(row, vertex, budget) < 0:
                raise ExactInvariantError("Generated vertex violates an exact processed halfspace")


def clip(poly, row, budget):
    budget.tick("clips")
    if row in poly.rows:
        return poly
    rows = poly.rows + (row,)
    if len(rows) > budget.limits.max_constraints:
        budget.exhausted("Processed halfspace bound exceeded")
    if poly.status != "full_dimensional":
        # Intersections cannot restore ambient dimension. Do not claim that
        # inherited vertices completely describe a subsequently clipped face.
        return Polytope(poly.n, (), rows, "subset_of_zero_measure_region",
                        poly.dimension_upper_bound, poly.unprocessed_constraints)
    values = [slack(row, v, budget) for v in poly.vertices]
    inside = [i for i, value in enumerate(values) if value > 0]
    boundary = [i for i, value in enumerate(values) if value == 0]
    outside = [i for i, value in enumerate(values) if value < 0]
    if not outside:
        return replace(poly, rows=rows)
    if not inside:
        vertices = tuple(poly.vertices[i] for i in boundary)
        if not vertices:
            return Polytope(poly.n, (), rows, "empty", -1)
        origin = vertices[0]
        dimension = rank([tuple(budget.sub(x, y) for x, y in zip(v, origin))
                          for v in vertices[1:]], budget)
        if dimension >= poly.d:
            raise ExactInvariantError("Supporting-cut face incorrectly has full dimension")
        return Polytope(poly.n, vertices, rows, "lower_dimensional_zero", dimension)
    vertices = {poly.vertices[i] for i in inside + boundary}
    active = [frozenset(j for j, h in enumerate(poly.rows)
                        if slack(h, v, budget) == 0) for v in poly.vertices]
    for i in inside:
        for j in outside:
            budget.tick("pair_checks")
            common = active[i] & active[j]
            # In the current full-dimensional polytope, a 1-face is exactly a
            # common active face of codimension d-1. Future rows are not used.
            if rank([poly.rows[k].a for k in common], budget) != poly.d - 1:
                continue
            t = budget.div(values[i], budget.sub(values[i], values[j]))
            if not 0 < t < 1:
                raise ExactInvariantError("Edge/cut intersection is not between its endpoints")
            a, b = poly.vertices[i], poly.vertices[j]
            vertex = tuple(budget.add(x, budget.mul(t, budget.sub(y, x)))
                           for x, y in zip(a, b))
            if slack(row, vertex, budget) != 0:
                raise ExactInvariantError("Edge intersection is not exactly on its cut")
            checked_vertices((vertex,), rows, budget)
            vertices.add(vertex)
            budget.vertices(len(vertices))
    if not vertices:
        raise ExactInvariantError("A strictly surviving full-dimensional clip has no vertices")
    result = replace(poly, vertices=tuple(sorted(vertices)), rows=rows)
    checked_vertices(result.vertices, rows, budget)
    return result


def simplex_polytope(n, constraints=(), *, equalities=(), budget=None):
    budget = budget or Budget()
    if type(n) is not int or not 2 <= n <= min(7, budget.limits.max_goals):
        raise UnsupportedGeometry("Only the configured 2..7 nonnegative weights with sum(w)=1 are supported")
    if len(constraints) + n > budget.limits.max_constraints or len(equalities) > budget.limits.max_constraints:
        budget.exhausted("Input halfspace count bound exceeded")
    # Extra explicit equalities must be exact, consistent multiples of sum=1.
    for a, b in equalities:
        if len(a) != n:
            raise UnsupportedGeometry("Equality dimension differs")
        aa = tuple(rational(x, budget) for x in a)
        bb = rational(b, budget)
        if any(x != aa[0] for x in aa) or bb != aa[0]:
            raise UnsupportedGeometry("Additional independent/inconsistent equalities are unsupported")
    # Validate every input before a possible zero-measure early termination.
    reduced = tuple(reduced_row(n, row, budget) for row in constraints)
    d = n - 1
    vertices = (tuple(Fraction(0) for _ in range(d)),) + tuple(
        tuple(Fraction(int(i == j)) for i in range(d)) for j in range(d))
    rows = tuple(Halfspace(tuple(Fraction(-int(i == j)) for i in range(d)), Fraction(0))
                 for j in range(d)) + (Halfspace((Fraction(1),) * d, Fraction(1)),)
    poly = Polytope(n, tuple(sorted(vertices)), rows, dimension_upper_bound=d)
    budget.vertices(len(vertices))
    for index, row in enumerate(reduced):
        poly = clip(poly, row, budget)
        if poly.status != "full_dimensional":
            return replace(poly, unprocessed_constraints=len(reduced) - index - 1)
    checked_vertices(poly.vertices, reduced + rows, budget)
    return poly


def coordinate_volume(poly, budget):
    if poly.status != "full_dimensional":
        return Fraction(0), {"simplices": 0, "faces": 0, "dimension_upper_bound": poly.dimension_upper_bound,
                             "status": poly.status, "unprocessed_constraints": poly.unprocessed_constraints,
                             "vertices_are_complete_for_final_region": poly.status in ("empty", "lower_dimensional_zero") and not poly.unprocessed_constraints}
    vertices = poly.vertices
    active = [frozenset(i for i, h in enumerate(poly.rows) if slack(h, v, budget) == 0)
              for v in vertices]
    dimensions = {}
    triangulations = {}
    face_count_before = budget.counts.get("faces", 0)

    def dimension(face):
        if face not in dimensions:
            origin = vertices[face[0]]
            dimensions[face] = rank([tuple(budget.sub(x, y) for x, y in zip(vertices[i], origin))
                                     for i in face[1:]], budget)
        return dimensions[face]

    def pulling(face):
        if face in triangulations:
            return triangulations[face]
        budget.tick("faces")
        k = dimension(face)
        if k == 0:
            if len(face) != 1:
                raise ExactInvariantError("Distinct vertices on a zero-dimensional face")
            result = (face,)
        else:
            facets = set()
            for h in range(len(poly.rows)):
                budget.tick("face_intersections")
                candidate = tuple(i for i in face if h in active[i])
                if candidate and candidate != face and dimension(candidate) == k - 1:
                    facets.add(candidate)
            apex = min(face)
            result_set = set()
            for facet in sorted(facets):
                if apex in facet:
                    continue
                for sub in pulling(facet):
                    simplex = tuple(sorted((apex, *sub)))
                    if len(simplex) != k + 1 or simplex in result_set:
                        raise ExactInvariantError("Invalid or duplicate pulling simplex")
                    budget.tick("simplices")
                    result_set.add(simplex)
            if not result_set:
                raise ExactInvariantError("Positive-dimensional face has no pulling triangulation")
            result = tuple(sorted(result_set))
        triangulations[face] = result
        return result

    face = tuple(range(len(vertices)))
    if dimension(face) != poly.d:
        raise ExactInvariantError("Full-dimensional state lacks full affine vertex rank")
    simplices = pulling(face)
    result = Fraction(0)
    for simplex in simplices:
        origin = vertices[simplex[0]]
        matrix = [tuple(budget.sub(x, y) for x, y in zip(vertices[i], origin)) for i in simplex[1:]]
        det = determinant(matrix, budget)
        if not det:
            raise ExactInvariantError("Zero-volume simplex in full-dimensional triangulation")
        result = budget.add(result, budget.div(abs(det), Fraction(math.factorial(poly.d))))
    if result <= 0:
        raise ExactInvariantError("Full-dimensional bounded polytope has nonpositive exact volume")
    return result, {"simplices": len(simplices), "faces": budget.counts.get("faces", 0) - face_count_before,
                    "dimension_upper_bound": poly.d, "status": poly.status,
                    "vertices_are_complete_for_final_region": True}


def positive_probability_float(value):
    if not 0 <= value <= 1:
        raise ExactInvariantError("Exact probability outside [0,1]")
    result = float(value)
    if value > 0 and result == 0:
        raise ProbabilityUnderflow("Positive exact mass would become floating zero")
    if not math.isfinite(result):
        raise ExactInvariantError("Nonfinite converted probability")
    return result


def split_polytope(parent, query, budget):
    row = reduced_row(parent.n, query, budget)
    if not any(row.a):
        raise UnsupportedGeometry("Affine-constant query: equality may have positive mass")
    return {"<": clip(parent, row, budget),
            ">": clip(parent, Halfspace(tuple(-x for x in row.a), -row.b), budget)}


def partition(n, constraints, query, *, equalities=(), limits=None, budget=None):
    """Exact common parent/children measures; Fractions remain authoritative.

    Direct kernel callers may supply test limits. The product entry point uses
    only resolved profile limits and shares its budget with input validation.
    A supported nonconstant cut has zero ambient equality mass.
    """
    if budget is None:
        budget = Budget(limits or Limits())
    elif limits is not None and limits != budget.limits:
        raise UnsupportedGeometry("Conflicting shared budget and limits")
    parent = simplex_polytope(n, constraints, equalities=equalities, budget=budget)
    parent_volume, parent_cost = coordinate_volume(parent, budget)
    if parent_volume == 0:
        raise ZeroParentVolume("No conditional probabilities for zero ambient parent volume")
    children = split_polytope(parent, query, budget)
    measured = {answer: (poly, *coordinate_volume(poly, budget))
                for answer, poly in children.items()}
    if budget.add(measured["<"][1], measured[">"][1]) != parent_volume:
        raise ExactInvariantError("Exact child volume sum differs from parent")
    output = {"n": n, "dimension": n - 1,
              "coordinate_measure": "dw0...dw[n-2]; common Euclidean factor sqrt(n) omitted",
              "parent_volume": parent_volume, "parent_vertices": len(parent.vertices),
              "parent_geometry": parent_cost, "input_constraint_count": len(constraints),
              "children": {}, "equality_probability": Fraction(0),
              "exact_child_sum_passed": True}
    for answer, (poly, volume, cost) in measured.items():
        probability = budget.div(volume, parent_volume)
        output["children"][answer] = {
            "volume": volume, "probability": probability,
            "probability_float": positive_probability_float(probability),
            "vertices": len(poly.vertices), "geometry": cost}
    output["budget"] = budget.report()
    return output


def constraint_key_arguments(key, *, budget=None):
    """Validate an explicit source simplex; never silently add a missing domain."""
    budget = budget or Budget()
    if not isinstance(key, (list, tuple)) or len(key) != 4:
        raise UnsupportedGeometry("Expected source constraint key (A,b,E,f)")
    a, b, e, f = key
    if len(a) != len(b) or len(e) != len(f) or not a:
        raise UnsupportedGeometry("Malformed constraint key")
    n = len(a[0])
    if not 2 <= n <= min(7, budget.limits.max_goals):
        raise UnsupportedGeometry("Constraint-key simplex dimension unsupported")
    if len(a) + n > budget.limits.max_constraints or len(e) > budget.limits.max_constraints:
        budget.exhausted("Input constraint count bound exceeded")
    aa = [tuple(rational(x, budget) for x in row) for row in a]
    bb = [rational(x, budget) for x in b]
    ee = [tuple(rational(x, budget) for x in row) for row in e]
    ff = [rational(x, budget) for x in f]
    if any(len(row) != n for row in (*aa, *ee)):
        raise UnsupportedGeometry("Ragged source constraint normals")
    for i in range(n):
        if not any(rhs == 0 and row[i] < 0
                   and all(x == 0 for j, x in enumerate(row) if j != i)
                   for row, rhs in zip(aa, bb)):
            raise UnsupportedGeometry("Source constraint key lacks explicit simplex nonnegativity")
    if not any(row[0] != 0 and all(x == row[0] for x in row) and rhs == row[0]
               for row, rhs in zip(ee, ff)):
        raise UnsupportedGeometry("Source constraint key lacks explicit sum(w)=1 equality")
    if any(any(x != row[0] for x in row) or rhs != row[0]
           for row, rhs in zip(ee, ff)):
        raise UnsupportedGeometry("Additional independent/inconsistent equalities are unsupported")
    return n, list(zip(aa, bb)), list(zip(ee, ff))


def ratio_query(n, query, *, budget=None):
    budget = budget or Budget()
    i, j = query["goal_index_a"], query["goal_index_b"]
    if type(i) is not int or type(j) is not int or i == j or not 0 <= i < n or not 0 <= j < n:
        raise UnsupportedGeometry("Invalid ratio query indices")
    value = rational(query["value"], budget)
    if value <= 0:
        raise UnsupportedGeometry("Positive finite ratio threshold required")
    row = [Fraction(0)] * n
    row[i], row[j] = Fraction(1), -value
    return row, Fraction(0)


def _profile_budget():
    values = resolved_numerical_profile()["values"]["simplex_partition_recovery"]
    expected = {entry.name for entry in fields(Limits)}
    if not isinstance(values, dict) or set(values) != expected:
        raise UnsupportedGeometry("Closed simplex recovery profile fields differ")
    return Budget(Limits(**values))


def _recovery_error(error, budget, *, reason=None):
    reason = reason or error.code
    failure = RecoveryGeometryError(f"simplex_partition:{reason}: {error}")
    failure.reason = reason
    failure.diagnostics = {
        "method": "bounded_exact_simplex_partition", "reason": reason,
        "work": budget.report() if budget is not None else None}
    return failure


def recover_probabilities(system, query):
    """Bounded exact recovery of one partition after native geometry fails.

    Requires explicit source rows proving sum(w)=1 and every w_i>=0, 2<=n<=
    the resolved max_goals<=7, and no other independent explicit equality.
    All original Binary64 coefficients are retained as exact Fractions. Parent
    and both children share x=(w0,...,w[n-2]) coordinates, one work budget and
    exact pulling volumes. The exact child sum must equal its parent before
    probability conversion. Caps, exact invariants, zero parent measure and
    positive float underflow fail closed, never returning approximate zero.
    No original constraint, policy, source, oracle or run state is changed.
    """
    try:
        budget = _profile_budget()
    except (UnsupportedGeometry, KeyError, TypeError) as error:
        raise _recovery_error(error, None, reason="invalid_recovery_profile") from error
    try:
        n, constraints, equalities = constraint_key_arguments(system.key, budget=budget)
        if system.variable_count != n:
            raise UnsupportedGeometry("System variable count differs from its key")
        cut = ratio_query(n, {"goal_index_a": query.goal_index_a,
                              "goal_index_b": query.goal_index_b,
                              "value": query.value}, budget=budget)
        result = partition(n, constraints, cut, equalities=equalities, budget=budget)
    except UnsupportedGeometry as error:
        failure = RecoveryNotApplicable(str(error))
        failure.reason = error.code
        failure.diagnostics = {"method": "bounded_exact_simplex_partition",
                               "reason": error.code, "work": budget.report()}
        raise failure from error
    except ExactPartitionError as error:
        raise _recovery_error(error, budget) from error
    recovered = RecoveredProbabilities({
        "<": result["children"]["<"]["probability_float"],
        "=": 0.0,
        ">": result["children"][">"]["probability_float"]})
    recovered.recovery_diagnostics = {
        "method": "bounded_exact_simplex_partition", "work": result["budget"],
        "exact_child_sum_passed": True, "parent_vertices": result["parent_vertices"],
        "child_vertices": {answer: child["vertices"] for answer, child in result["children"].items()}}
    return recovered
