"""Small mathematical optimization values without backend dependencies."""
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class LinearResult:
    status: Literal["optimal", "infeasible", "unbounded"]
    objective_sense: Literal["min", "max"]
    optimal_value: float | None = None
    solver_status_code: int | None = None
    solver_message: str | None = None
