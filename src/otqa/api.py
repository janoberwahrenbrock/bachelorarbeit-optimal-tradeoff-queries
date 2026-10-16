"""Public synchronous solver entry point with lazy numerical imports."""
from __future__ import annotations

from collections.abc import Callable, Sequence

from .config import AlgorithmPolicy, QueryBudget, SolverExecution
from .continuation import SolveContinuation
from .models import Answer, AnsweredQuery, Problem, Query, SolveResult, SolverEvent


def solve(
    problem: Problem,
    policy: AlgorithmPolicy,
    answer_provider: Callable[[Query], Answer],
    *,
    budget: QueryBudget = QueryBudget(),
    execution: SolverExecution = SolverExecution(),
    initial_answers: Sequence[AnsweredQuery] = (),
    continuation: SolveContinuation | None = None,
    recorder: Callable[[SolverEvent], None] | None = None,
    observer: Callable[[SolverEvent], None] | None = None,
) -> SolveResult:
    """Solve with one accepted answer at a time and owned planning resources."""
    from .solver import solve_with_session
    return solve_with_session(problem, policy, answer_provider, budget=budget,
                              execution=execution, initial_answers=initial_answers,
                              continuation=continuation, recorder=recorder, observer=observer)
