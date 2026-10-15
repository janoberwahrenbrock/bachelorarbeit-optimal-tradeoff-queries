"""Prepared mathematical state types, independent of generators and runtime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from otqa.models.numerical import LinearResult

from .frozen import FrozenMapping

if TYPE_CHECKING:
    from otqa.config import AlgorithmPolicy
    from otqa.models import AnsweredQuery, Problem
    from otqa.geometry import ConstraintSystem


@dataclass(frozen=True)
class RatioInterval:
    lower: LinearResult
    upper: LinearResult


@dataclass(frozen=True)
class GoalPairRatioIntervals:
    goal_index_a: int
    goal_index_b: int
    intervals_by_candidate: dict[int, RatioInterval]

    def __post_init__(self):
        if not isinstance(self.intervals_by_candidate, FrozenMapping):
            object.__setattr__(self, "intervals_by_candidate", FrozenMapping(self.intervals_by_candidate))


@dataclass(frozen=True)
class CandidateAnalysis:
    candidates: tuple[int, ...]
    ratio_intervals: tuple[GoalPairRatioIntervals, ...] | None = None
    candidate_volumes: dict[int, float] | None = None
    candidate_volume_shares: dict[int, float] | None = None

    def __post_init__(self):
        object.__setattr__(self, "candidates", tuple(self.candidates))
        if self.ratio_intervals is not None:
            object.__setattr__(self, "ratio_intervals", tuple(self.ratio_intervals))
        for name in ("candidate_volumes", "candidate_volume_shares"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, FrozenMapping):
                object.__setattr__(self, name, FrozenMapping(value))


@dataclass(frozen=True)
class PreparedState:
    session_id: str
    problem: Problem
    policy: AlgorithmPolicy
    history: tuple[AnsweredQuery, ...]
    weight_space: ConstraintSystem
    is_feasible: bool
    analysis: CandidateAnalysis | None = None
    checked_candidates: tuple[int, ...] | None = None

    @property
    def candidates(self):
        return () if self.analysis is None else self.analysis.candidates

    @property
    def candidate_analysis(self):
        return self.analysis
