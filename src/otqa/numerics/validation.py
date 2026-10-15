"""Guarded continuous primal validation with SciPy's exact error fallback.

The common successful continuous case avoids the unused semi-continuous
allowance. Bounds, objective, all slacks and equality residuals are checked.
Errors and unfamiliar inputs are delegated to the actual SciPy checker.
"""
import hashlib
import inspect

import numpy as np

try:
    from scipy.optimize._linprog_util import _check_result as CHECKER
except (ImportError, AttributeError):
    CHECKER = None

_CODE = getattr(CHECKER, "__code__", None)
_ISCLOSE = np.isclose
try:
    SOURCE_VERIFIED = hashlib.sha256(inspect.getsource(CHECKER).encode()).hexdigest() in {
        "599e4d0380edaa1fb91d5de7d657266c36de3f92c0534811bece19c305cfa17b"}
except (OSError, TypeError):
    SOURCE_VERIFIED = False


def continuous_check(checker, x, fun, status, slack, con, bounds, tol, message):
    arguments = x, fun, status, slack, con, bounds, tol, message, None
    arrays = (x, slack, con)
    supported = (SOURCE_VERIFIED and checker is CHECKER and checker.__code__ is _CODE
                 and checker.__globals__.get("np") is np and np.isclose is _ISCLOSE
                 and type(status) is int and type(message) is str
                 and type(fun) is float and type(tol) is float and tol == 1e-9
                 and all(type(array) is np.ndarray and array.dtype == np.dtype(np.float64)
                         and array.ndim == 1 and array.flags.c_contiguous
                         and array.strides[0] >= 0 for array in arrays)
                 and type(bounds) is np.ndarray and bounds.dtype == np.dtype(np.float64)
                 and bounds.shape == (len(x), 2) and bounds.flags.c_contiguous
                 and bounds.strides[0] >= 0 and bounds.strides[1] >= 0)
    if not supported:
        return checker(*arguments)
    effective_tol = np.sqrt(tol) * 10
    contains_nan = (np.isnan(x).any() or np.isnan(fun)
                    or np.isnan(slack).any() or np.isnan(con).any())
    if contains_nan:
        feasible = False
    else:
        valid_bounds = (x >= bounds[:, 0] - effective_tol) & (x <= bounds[:, 1] + effective_tol)
        invalid_bounds = not np.all(valid_bounds)
        invalid_slack = status != 3 and (slack < -effective_tol).any()
        invalid_con = status != 3 and (np.abs(con) > effective_tol).any()
        feasible = not (invalid_bounds or invalid_slack or invalid_con)
    if (status == 0 and not feasible) or (status == 2 and feasible):
        return checker(*arguments)
    return status, message
