"""Continuous LP backend with the method's fixed retry and validation rules."""
from __future__ import annotations

from typing import Any

from scipy.optimize import linprog

from otqa.models.numerical import LinearResult as LinearResult

LP_OPTIONS = {"primal_feasibility_tolerance": 1e-10,
              "dual_feasibility_tolerance": 1e-10, "disp": False}


def classify_failure(status: int, message: str) -> str | None:
    if status == 2:
        return "infeasible"
    if status == 3:
        return "unbounded"
    message = message.lower()
    if "model_status is infeasible" in message or "primal_status is infeasible" in message:
        return "infeasible"
    if "model_status is unbounded" in message:
        return "unbounded"
    return None


class LinearProgramBackend:
    """Own one optional cold-model HiGHS adapter; never share native handles."""
    def __init__(self, *, native: bool = True):
        from .native import ColdHighs
        self.native = ColdHighs() if native else None
        self.calls = 0

    def _solve(self, arguments: dict[str, Any]):
        self.calls += 1
        result = self.native.try_solve(arguments) if self.native is not None else None
        return linprog(**arguments) if result is None else result

    def solve(self, *, c, A_ub=None, b_ub=None, A_eq=None, b_eq=None,
              bounds=None, method="highs", options=None):
        arguments = dict(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                         bounds=bounds, method=method,
                         options=dict(LP_OPTIONS if options is None else options))
        result = self._solve(arguments)
        if result.success:
            return result
        failure = classify_failure(int(result.status), str(result.message))
        if failure != "unbounded":
            retry = {**arguments, "options": {**LP_OPTIONS, "presolve": False}}
            alternative = self._solve(retry)
            if alternative.success or classify_failure(int(alternative.status), str(alternative.message)):
                return alternative
            for fallback in ("highs-ds", "highs-ipm"):
                if fallback != method:
                    alternative = self._solve({**retry, "method": fallback})
                    if alternative.success or classify_failure(int(alternative.status), str(alternative.message)):
                        return alternative
        return result

    def close(self):
        if self.native is not None:
            self.native.close()
