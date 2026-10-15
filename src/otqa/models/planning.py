"""Immutable planning evidence, separate from runtime documents.

Expected candidates and effective loss are distinct: a confidence terminal
can retain several candidates while having loss one. Missing lazy values
are absent from a profile rather than represented by zero.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real

from .core import Answer, Query


def _finite(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(float(value)):
        raise ValueError(f"{name} must be finite")
    return float(value)


@dataclass(frozen=True, slots=True)
class BranchEvaluation:
    answer: Answer
    probability: float
    expected_terminal_candidates: float
    candidate_count: int | None
    is_feasible: bool
    expected_terminal_loss: float | None = None
    stop_reason: str | None = None
    maximum_volume_share: float | None = None
    expected_followup_queries: float | None = None


@dataclass(frozen=True, slots=True)
class QueryEvaluation:
    query: Query
    expected_terminal_candidates: float
    branches: tuple[BranchEvaluation, ...]
    query_source: str = "unknown"
    lexicographic_profile: tuple[float, ...] = ()
    expected_terminal_loss: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "branches", tuple(self.branches))
        object.__setattr__(self, "lexicographic_profile", tuple(self.lexicographic_profile))


@dataclass(frozen=True, slots=True)
class Continuation:
    answer: Answer
    probability: float
    candidate_count: int
    expected_terminal_candidates: float
    evaluation: QueryEvaluation | None
    expected_terminal_loss: float | None = None
    stop_reason: str | None = None
    maximum_volume_share: float | None = None
    expected_queries: float | None = None
    continuations: tuple[Continuation, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "continuations", tuple(self.continuations))


@dataclass(frozen=True, slots=True)
class FixedScore:
    expected_terminal_candidates: float
    expected_terminal_loss: float
    lexicographic_profile: tuple[float, ...]
    expected_queries: float | None = None

    def __post_init__(self) -> None:
        for name in ("expected_terminal_candidates", "expected_terminal_loss"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        object.__setattr__(self, "lexicographic_profile", tuple(_finite(value, "lexicographic value")
                                                             for value in self.lexicographic_profile))
        if not self.lexicographic_profile:
            raise ValueError("a fixed score requires its actually evaluated profile")
        if self.expected_queries is not None:
            value = _finite(self.expected_queries, "expected_queries")
            if value <= 0.0:
                raise ValueError("expected_queries must be positive")
            object.__setattr__(self, "expected_queries", value)


@dataclass(frozen=True, slots=True)
class EfficiencyScore:
    expected_terminal_candidates: float
    expected_terminal_loss: float
    expected_queries: float
    gain: float
    rate: float

    def __post_init__(self) -> None:
        for name in ("expected_terminal_candidates", "expected_terminal_loss", "expected_queries", "gain", "rate"):
            object.__setattr__(self, name, _finite(getattr(self, name), name))
        if self.expected_queries <= 0.0:
            raise ValueError("expected_queries must be positive")


@dataclass(frozen=True, slots=True)
class HorizonEvidence:
    horizon: int
    evaluations: tuple[QueryEvaluation, ...]
    selected_query: Query | None
    selected_score: FixedScore | EfficiencyScore | None = None
    selected_answer_probabilities: tuple[tuple[Answer, float], ...] = ()
    selected_continuations: tuple[Continuation, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "evaluations", tuple(self.evaluations))
        object.__setattr__(self, "selected_answer_probabilities", tuple(tuple(pair) for pair in self.selected_answer_probabilities))
        object.__setattr__(self, "selected_continuations", tuple(self.selected_continuations))


@dataclass(frozen=True, slots=True)
class PlanningDecision:
    query: Query
    horizon: int
    score: FixedScore | EfficiencyScore
    answer_probabilities: tuple[tuple[Answer, float], ...]
    evaluation: QueryEvaluation
    continuations: tuple[Continuation, ...] = ()
    horizons: tuple[HorizonEvidence, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "answer_probabilities", tuple(tuple(pair) for pair in self.answer_probabilities))
        object.__setattr__(self, "continuations", tuple(self.continuations))
        object.__setattr__(self, "horizons", tuple(self.horizons))


@dataclass(frozen=True, slots=True)
class NoQuery:
    candidate_count: int
    is_feasible: bool = True
    horizons: tuple[HorizonEvidence, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "horizons", tuple(self.horizons))


def query_identity(query: Query) -> tuple[int, int, float]:
    """Original indices and binary64 value; no rounding or display identity."""
    return query.goal_index_a, query.goal_index_b, query.value


@dataclass(frozen=True, slots=True)
class PolicyOption:
    """A complete child policy, including all mandated continuation levels."""

    evaluation: QueryEvaluation | None
    expected_terminal_candidates: float
    expected_terminal_loss: float
    expected_queries: float
    continuations: tuple[Continuation, ...] = ()
    stop_reason: str | None = None
    maximum_volume_share: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "continuations", tuple(self.continuations))


def continuation_identity(child: Continuation) -> tuple:
    return (
        query_identity(child.evaluation.query) if child.evaluation else (-1, -1, 0.0),
        tuple(continuation_identity(item) for item in child.continuations),
    )


def option_identity(option: PolicyOption) -> tuple:
    return (
        query_identity(option.evaluation.query) if option.evaluation else (-1, -1, 0.0),
        tuple(continuation_identity(item) for item in option.continuations),
    )
