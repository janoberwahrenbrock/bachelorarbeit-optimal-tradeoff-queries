"""Pure actual-horizon transitions; no planner, callbacks, IO, or native state."""
from __future__ import annotations

from .config import AlgorithmPolicy
from .errors import InputValidationError, PlanningInvariantError
from .models.execution import ExecutionCursor, PlanningAttempt, PlanningCycle
from .models.planning import PlanningDecision


def initial_cursor(policy: AlgorithmPolicy, answered_total: int) -> ExecutionCursor:
    """An imported answer history starts a fresh full block."""
    return ExecutionCursor(answered_total, policy.depth)


def validate_cursor(policy: AlgorithmPolicy, cursor: ExecutionCursor, answered_total: int) -> None:
    if not isinstance(cursor, ExecutionCursor):
        raise InputValidationError('continuation needs an ExecutionCursor')
    if cursor.answered_total != answered_total or cursor.remaining_depth > policy.depth:
        raise InputValidationError('execution cursor differs from its history or maximum depth')
    if policy.horizon_execution != 'countdown' and cursor.remaining_depth != policy.depth:
        raise InputValidationError('receding execution always requests the configured maximum depth')


def validate_attempt(policy: AlgorithmPolicy, attempt: PlanningAttempt, requested_depth: int,
                     candidate_count: int) -> None:
    """Guard the planner/execution boundary without recomputing any plan."""
    if not isinstance(attempt, PlanningAttempt) or attempt.requested_depth != requested_depth:
        raise PlanningInvariantError('planner did not return its explicit requested depth')
    expected = (requested_depth,) if policy.query_strategy == 'fixed' else tuple(range(1, requested_depth + 1))
    if attempt.evaluated_horizons != expected:
        raise PlanningInvariantError('planner did not cover the required actual horizons')
    plan, progress = attempt.selected_plan, attempt.selected_progress
    if plan is not None:
        if plan.horizon not in expected or progress is None or not progress.admissible:
            raise PlanningInvariantError('selected actual plan is not admissible at the requested horizon')
        basis = 'candidate_count' if policy.planning_evaluation == 'candidate_count' else 'effective_loss'
        terminal = plan.score.expected_terminal_candidates if basis == 'candidate_count' else plan.score.expected_terminal_loss
        if (progress.basis != basis or progress.starting_value != float(candidate_count)
                or progress.expected_terminal_value != terminal
                or _threshold_key(progress.threshold) != _threshold_key(policy.min_expected_progress)):
            raise PlanningInvariantError('selected progress evidence differs from the actual policy or score')
    if attempt.outcome == 'insufficient_expected_progress' and policy.min_expected_progress is None:
        raise PlanningInvariantError('disabled progress checking cannot reject a plan for its gain')


def _threshold_key(value: float | None):
    return None if value is None else value.hex()


def requires_full_retry(policy: AlgorithmPolicy, cursor: ExecutionCursor,
                        attempt: PlanningAttempt) -> bool:
    return (policy.horizon_execution == 'countdown'
            and cursor.remaining_depth < policy.depth
            and attempt.outcome in ('no_query', 'insufficient_expected_progress'))


def cursor_after_answer(policy: AlgorithmPolicy, cursor: ExecutionCursor,
                         decision: PlanningDecision) -> ExecutionCursor:
    remaining = policy.depth
    if policy.horizon_execution == 'countdown' and decision.horizon > 1:
        remaining = decision.horizon - 1
    return ExecutionCursor(cursor.answered_total + 1, remaining)


def resolve_cycle(policy: AlgorithmPolicy, cursor: ExecutionCursor,
                  attempts: tuple[PlanningAttempt, ...]) -> PlanningCycle:
    """Resolve one request and, only where mandated, its one full retry."""
    attempts = tuple(attempts)
    if not 1 <= len(attempts) <= 2 or attempts[0].requested_depth != cursor.remaining_depth:
        raise PlanningInvariantError('actual cycle does not begin at the current cursor')
    retry = requires_full_retry(policy, cursor, attempts[0])
    if retry != (len(attempts) == 2):
        raise PlanningInvariantError('a shortened rejected plan requires exactly one full retry')
    if len(attempts) == 2 and attempts[1].requested_depth != policy.depth:
        raise PlanningInvariantError('countdown replacement must use the full maximum depth')
    final = attempts[-1]
    proposed = cursor_after_answer(policy, cursor, final.selected_plan) if final.selected_plan is not None else None
    return PlanningCycle(cursor, attempts, final.selected_plan, final.outcome,
                         attempts[0].outcome if retry else None, proposed)
