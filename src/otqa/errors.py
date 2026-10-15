"""Stable failure categories for the solver and its application adapters."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.results import PartialContext


class SolverError(Exception):
    """A failed call, optionally carrying its immutable accepted partial state."""

    def __init__(self, message: str, *, context: PartialContext | None = None) -> None:
        super().__init__(message)
        self.context = context

    @property
    def partial_context(self) -> PartialContext | None:
        return self.context


class InputValidationError(SolverError, ValueError):
    """The requested problem, policy or application input is invalid."""


class InvalidAnswerError(InputValidationError):
    """A provider returned something other than an answer literal."""


class InfeasibleStateError(SolverError):
    """Accepted answers leave no feasible weight state."""


class NumericalError(SolverError):
    """A numerical backend could not produce a validated result."""


class PlanningInvariantError(SolverError, RuntimeError):
    """A planning or state ownership invariant was violated."""


class AnswerProviderError(SolverError):
    """The answer provider failed; its original exception is chained."""


class RecorderError(SolverError):
    """Required synchronous recording failed."""


class ObserverError(SolverError):
    """An injected observer failed."""


class ExecutionContextError(SolverError):
    """The requested execution context or owned worker lifecycle failed."""


class EvaluationCaptureError(SolverError):
    """A bounded internal diagnostic capture could not complete."""
