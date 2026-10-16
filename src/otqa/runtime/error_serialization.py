"""Neutral exception-to-wire projection; no CaseProcess or solver imports."""
from __future__ import annotations

import traceback
from dataclasses import asdict

from .storage import PersistenceError


def error_wire(error: BaseException, stage="controller") -> dict:
    codes = {"InputValidationError": ("invalid_input", "input"), "InvalidAnswerError": ("invalid_answer", "provider"),
        "InfeasibleStateError": ("infeasible_state", "numerics"), "NumericalError": ("numerical_failure", "numerics"),
        "PlanningInvariantError": ("planning_invariant", "planning"), "AnswerProviderError": ("answer_provider", "provider"),
        "ObserverError": ("observer", "observer"), "RecorderError": ("persistence_failure", "persistence"),
        "PersistenceError": ("persistence_failure", "persistence"), "ExecutionContextError": ("context_unavailable", "worker")}
    code, resolved_stage = codes.get(type(error).__name__, ("unknown", stage))
    # A runtime optional sink may fail while durably publishing its mandatory
    # diagnostic. The public SDK correctly wraps observer exceptions; preserve
    # the underlying persistence classification at the runtime boundary.
    cause = error.__cause__
    if type(error).__name__ == "ObserverError" and isinstance(cause, PersistenceError):
        code, resolved_stage = "persistence_failure", "persistence"
    context = {}
    partial = getattr(error, "partial_context", None)
    if partial is not None:
        context["memory_query_counts"] = asdict(partial.query_counts)
        context["memory_answer_count"] = len(partial.answers)
        if getattr(partial, 'execution_cursor', None) is not None:
            context['memory_execution_cursor'] = asdict(partial.execution_cursor)
        pending = getattr(partial, 'pending_cycle', None)
        if pending is not None:
            context['memory_pending_planning'] = {'cursor_before': asdict(pending.cursor_before),
                'completed_attempts': len(pending.attempts), 'active_attempt_index': pending.active_attempt_index,
                'requested_depth': pending.requested_depth}
    if getattr(error, "cleanup_errors", None):
        context["cleanup_errors"] = list(error.cleanup_errors)
    return {"code": code, "type": type(error).__name__, "message": str(error) or type(error).__name__,
        "traceback": "".join(traceback.format_exception(error)), "stage": resolved_stage, "context": context}

