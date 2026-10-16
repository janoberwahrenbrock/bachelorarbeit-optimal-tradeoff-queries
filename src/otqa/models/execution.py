"""Immutable actual-execution evidence, independent of geometry and runtime."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ..errors import InputValidationError
from .core import finite_float, integer
from .planning import PlanningDecision


PlanningOutcome = Literal['available', 'no_query', 'insufficient_expected_progress']
_OUTCOMES = ('available', 'no_query', 'insufficient_expected_progress')


@dataclass(frozen=True, slots=True)
class ExecutionCursor:
    """The next horizon at an accepted-answer boundary, never a durable claim."""

    answered_total: int
    remaining_depth: int

    def __post_init__(self) -> None:
        object.__setattr__(self, 'answered_total', integer(self.answered_total, name='answered_total', minimum=0))
        depth = integer(self.remaining_depth, name='remaining_depth', minimum=1)
        if depth > 3:
            raise InputValidationError('remaining_depth must be at most three')
        object.__setattr__(self, 'remaining_depth', depth)


@dataclass(frozen=True, slots=True)
class ProgressEvidence:
    basis: Literal['candidate_count', 'effective_loss']
    starting_value: float
    expected_terminal_value: float
    expected_progress: float
    threshold: float | None
    comparison: Literal['strict_greater'] = 'strict_greater'
    admissible: bool = True

    def __post_init__(self) -> None:
        if self.basis not in ('candidate_count', 'effective_loss') or self.comparison != 'strict_greater':
            raise ValueError('unknown progress evidence basis or comparison')
        for name in ('starting_value', 'expected_terminal_value', 'expected_progress'):
            object.__setattr__(self, name, finite_float(getattr(self, name), name=name))
        if self.threshold is not None:
            threshold = finite_float(self.threshold, name='progress threshold')
            if threshold < 0:
                raise ValueError('progress threshold must be nonnegative')
            object.__setattr__(self, 'threshold', threshold)
        if type(self.admissible) is not bool:
            raise ValueError('progress admissibility must be boolean')
        if self.expected_progress != self.starting_value - self.expected_terminal_value:
            raise ValueError('progress evidence does not use the stored subtraction')
        if self.admissible != (self.threshold is None or self.expected_progress > self.threshold):
            raise ValueError('progress evidence disagrees with its strict threshold')


@dataclass(frozen=True, slots=True)
class HorizonSelectionEvidence:
    horizon: int
    generated_query_count: int
    evaluated_query_count: int
    outcome: PlanningOutcome
    selected_plan: PlanningDecision | None = None
    selected_progress: ProgressEvidence | None = None
    best_progress_witness: PlanningDecision | None = None
    best_progress: ProgressEvidence | None = None

    def __post_init__(self) -> None:
        integer(self.horizon, name='horizon', minimum=1)
        integer(self.generated_query_count, name='generated_query_count', minimum=0)
        integer(self.evaluated_query_count, name='evaluated_query_count', minimum=0)
        if self.horizon > 3 or self.evaluated_query_count > self.generated_query_count:
            raise ValueError('invalid horizon or query coverage')
        if self.outcome not in _OUTCOMES:
            raise ValueError('unknown horizon outcome')
        if (self.selected_plan is not None) != (self.outcome == 'available'):
            raise ValueError('available horizon must have exactly one selected plan')
        if (self.selected_progress is None) != (self.selected_plan is None):
            raise ValueError('selected horizon plan needs progress evidence')
        if (self.best_progress_witness is None) != (self.best_progress is None):
            raise ValueError('horizon progress witness needs matching evidence')


@dataclass(frozen=True, slots=True)
class PlanningAttempt:
    """One explicit mathematical request, containing no execution phase."""

    requested_depth: int
    evaluated_horizons: tuple[int, ...]
    outcome: PlanningOutcome
    selected_plan: PlanningDecision | None = None
    selected_progress: ProgressEvidence | None = None
    best_progress_witness: PlanningDecision | None = None
    horizon_evidence: tuple[HorizonSelectionEvidence, ...] = ()

    def __post_init__(self) -> None:
        integer(self.requested_depth, name='requested_depth', minimum=1)
        object.__setattr__(self, 'evaluated_horizons', tuple(self.evaluated_horizons))
        object.__setattr__(self, 'horizon_evidence', tuple(self.horizon_evidence))
        if self.requested_depth > 3 or self.outcome not in _OUTCOMES:
            raise ValueError('invalid requested depth or planning outcome')
        if not self.evaluated_horizons or len(set(self.evaluated_horizons)) != len(self.evaluated_horizons):
            raise ValueError('planning request needs distinct evaluated horizons')
        if any(type(depth) is not int or not 1 <= depth <= self.requested_depth for depth in self.evaluated_horizons):
            raise ValueError('evaluated horizon lies outside the explicit request')
        if (self.selected_plan is not None) != (self.outcome == 'available'):
            raise ValueError('available attempt must have exactly one selected plan')
        if (self.selected_progress is None) != (self.selected_plan is None):
            raise ValueError('selected plan needs progress evidence')


@dataclass(frozen=True, slots=True)
class PlanningCycle:
    """A resolved actual decision, including a possible one-time full retry."""

    cursor_before: ExecutionCursor
    attempts: tuple[PlanningAttempt, ...]
    selected_plan: PlanningDecision | None
    outcome: PlanningOutcome
    restart_reason: Literal['no_query', 'insufficient_expected_progress'] | None = None
    proposed_cursor_after_answer: ExecutionCursor | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'attempts', tuple(self.attempts))
        if not 1 <= len(self.attempts) <= 2:
            raise ValueError('an actual planning cycle has one or two attempts')
        if self.outcome != self.attempts[-1].outcome or self.selected_plan != self.attempts[-1].selected_plan:
            raise ValueError('cycle differs from its final attempt')
        if (self.proposed_cursor_after_answer is not None) != (self.outcome == 'available'):
            raise ValueError('only a selected actual query proposes an answer cursor')
        if len(self.attempts) == 1 and self.restart_reason is not None:
            raise ValueError('one attempt cannot claim a restart')
        if len(self.attempts) == 2 and self.restart_reason != self.attempts[0].outcome:
            raise ValueError('restart must bind the rejected first attempt')


@dataclass(frozen=True, slots=True)
class PendingPlanningCycle:
    """Partial execution evidence; an active attempt is not a completed plan."""

    cursor_before: ExecutionCursor
    attempts: tuple[PlanningAttempt, ...] = ()
    active_attempt_index: int | None = None
    requested_depth: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'attempts', tuple(self.attempts))
        if len(self.attempts) > 2:
            raise ValueError('a pending cycle has at most two actual attempts')
        if (self.active_attempt_index is None) != (self.requested_depth is None):
            raise ValueError('active attempt index and depth must occur together')
        if self.active_attempt_index is not None and self.active_attempt_index != len(self.attempts) + 1:
            raise ValueError('active attempt must follow completed attempts')
        if self.active_attempt_index is not None:
            integer(self.requested_depth, name='requested_depth', minimum=1)
            if self.active_attempt_index > 2 or self.requested_depth > 3:
                raise ValueError('pending attempt lies outside the actual cycle')
