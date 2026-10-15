"""Guarded reuse of SciPy's own HiGHS binding, always as a cold solve.

This is a setup optimization: each objective reloads the pristine LP template
and clears all solver state. Unsupported capabilities use public ``linprog``.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import os
from threading import get_ident

import numpy as np
from scipy.optimize import OptimizeResult
from scipy.sparse import csc_array, issparse

from .validation import continuous_check

try:
    from scipy.sparse import get_index_dtype
except ImportError:
    get_index_dtype = None
try:
    from scipy.optimize._highspy import _core as highs
    from scipy.optimize._linprog_highs import _highs_to_scipy_status_message
    from scipy.optimize._linprog_util import _LPProblem, _clean_inputs, _check_result
    AVAILABLE = all(hasattr(highs._Highs, name) for name in (
        "clearSolver", "clearModel", "passOptions", "passModel", "run",
        "getInfo", "getSolution", "getBasis", "getModelStatus"))
except (ImportError, AttributeError):
    AVAILABLE = False

_INITIAL_CLEANER = globals().get("_clean_inputs")
_KEYWORDS = {"c", "A_ub", "b_ub", "A_eq", "b_eq", "bounds", "method", "options"}
_OPTIONS = {"primal_feasibility_tolerance", "dual_feasibility_tolerance", "disp", "presolve"}


def _array_key(array):
    return array.shape, array.dtype.str, array.tobytes()


def _require_ok(status):
    if status == highs.HighsStatus.kError:
        raise RuntimeError("native HiGHS operation failed")


def _matrix_csc(a_ub, a_eq):
    dense = np.vstack((a_ub, a_eq))
    if get_index_dtype is None or dense.dtype != np.dtype(np.float64):
        matrix = csc_array(dense)
        return matrix.data, matrix.indices, matrix.indptr
    transposed = dense.T
    columns, rows = transposed.nonzero()
    index_dtype = get_index_dtype(maxval=max(*dense.shape, len(rows)))
    indices = np.array(rows, dtype=index_dtype, copy=True)
    indptr = np.empty(dense.shape[1] + 1, dtype=index_dtype)
    indptr[0] = 0
    np.cumsum(np.bincount(columns, minlength=dense.shape[1]),
              dtype=index_dtype, out=indptr[1:])
    return transposed[columns, rows], indices, indptr


def _problem(arguments):
    return _LPProblem(arguments["c"], arguments.get("A_ub"), arguments.get("b_ub"),
                      arguments.get("A_eq"), arguments.get("b_eq"),
                      arguments.get("bounds"), None, None)


def _clean(arguments):
    """Validate and copy ordinary continuous inputs; defer unusual cases."""
    def fallback():
        return _clean_inputs(_problem(arguments))
    objective = arguments["c"]
    ordinary = (type(objective) is np.ndarray and objective.dtype == np.dtype(np.float64)
                and objective.ndim == 1 and objective.flags.c_contiguous)
    ordinary |= (type(objective) in (list, tuple)
                 and all(type(value) in (float, int) for value in objective))
    if _clean_inputs is not _INITIAL_CLEANER or not ordinary:
        return fallback()
    try:
        c = np.array(objective, dtype=np.float64, copy=True).squeeze()
    except (TypeError, ValueError, OverflowError):
        return fallback()
    if c.size == 1:
        c = c.reshape(-1)
    if c.ndim != 1 or c.size == 0 or not np.isfinite(c).all():
        return fallback()
    count = len(c)
    constraints = []
    for matrix_name, rhs_name in (("A_ub", "b_ub"), ("A_eq", "b_eq")):
        matrix, rhs = arguments.get(matrix_name), arguments.get(rhs_name)
        if matrix is None and rhs is None:
            constraints.extend((np.zeros((0, count)), np.array([], dtype=float)))
        elif (type(matrix) is np.ndarray and type(rhs) is np.ndarray
              and matrix.dtype == rhs.dtype == np.dtype(np.float64)
              and matrix.ndim == 2 and matrix.shape[1] == count
              and rhs.shape == (matrix.shape[0],)
              and matrix.flags.c_contiguous and rhs.flags.c_contiguous
              and np.isfinite(matrix).all() and np.isfinite(rhs).all()):
            constraints.extend((matrix.copy(order="K"), rhs.copy(order="K")))
        else:
            return fallback()
    bounds = arguments.get("bounds")
    if bounds is None:
        cleaned = np.empty((count, 2))
        cleaned[:, 0], cleaned[:, 1] = 0.0, np.inf
    elif type(bounds) is np.ndarray:
        if not (bounds.dtype == np.dtype(np.float64) and bounds.shape == (count, 2)
                and bounds.flags.c_contiguous and np.isfinite(bounds).all()):
            return fallback()
        cleaned = bounds.copy(order="K")
    elif type(bounds) in (list, tuple) and len(bounds) == count:
        cleaned = np.empty((count, 2))
        for row_index, row in enumerate(bounds):
            if type(row) not in (list, tuple) or len(row) != 2:
                return fallback()
            for column, value in enumerate(row):
                if value is None:
                    cleaned[row_index, column] = -np.inf if column == 0 else np.inf
                elif type(value) in (int, float):
                    try:
                        number = float(value)
                    except (ValueError, OverflowError):
                        return fallback()
                    if not np.isfinite(number):
                        return fallback()
                    cleaned[row_index, column] = number
                else:
                    return fallback()
    else:
        return fallback()
    return _LPProblem(c, *constraints, cleaned, None, None)


@dataclass
class _NativeModel:
    solver: object
    template: object
    options_key: tuple
    bytes: int


class ColdHighs:
    """Bounded native model/option storage with process and thread ownership."""
    def __init__(self):
        self.models = OrderedDict()
        self.options = OrderedDict()
        self.bytes = self.calls = self.hits = self.fallbacks = 0
        self.owner = os.getpid(), get_ident()

    def close(self):
        self.models.clear()
        self.options.clear()
        self.bytes = 0

    def _supported(self, arguments):
        if not AVAILABLE or arguments.keys() - _KEYWORDS:
            return False
        if arguments.get("method", "highs") not in {"highs", "highs-ds", "highs-ipm"}:
            return False
        if any(issparse(arguments.get(key)) for key in ("A_ub", "A_eq")):
            return False
        options = arguments.get("options") or {}
        if not isinstance(options, dict) or options.keys() - _OPTIONS:
            return False
        if options.get("disp", False) is not False or type(options.get("presolve", True)) is not bool:
            return False
        for key in ("primal_feasibility_tolerance", "dual_feasibility_tolerance"):
            value = options.get(key, 1e-7)
            if (isinstance(value, bool) or not isinstance(value, (float, int))
                    or not np.isfinite(value) or value < 1e-10):
                return False
        return True

    def _options(self, key):
        result = self.options.get(key)
        if result is None:
            method, presolve, primal, dual = key
            result = highs.HighsOptions()
            result.presolve = "on" if presolve else "off"
            if method != "highs":
                result.solver = "simplex" if method == "highs-ds" else "ipm"
            result.primal_feasibility_tolerance, result.dual_feasibility_tolerance = primal, dual
            result.output_flag = result.log_to_console = False
            result.highs_debug_level = int(highs.HighsDebugLevel.kHighsDebugLevelNone)
            result.simplex_strategy = int(highs.simplex_constants.SimplexStrategy.kSimplexStrategyDual)
            self.options[key] = result
            while len(self.options) > 32:
                self.options.popitem(last=False)
        self.options.move_to_end(key)
        return result

    def try_solve(self, arguments):
        self.calls += 1
        if self.owner != (os.getpid(), get_ident()) or not self._supported(arguments):
            self.fallbacks += 1
            return None
        try:
            return self._solve(arguments)
        except Exception:
            self.close()
            self.fallbacks += 1
            return None

    def _solve(self, arguments):
        problem = _clean(arguments)
        c, a_ub, b_ub, a_eq, b_eq, bounds, _, _ = problem
        options = arguments.get("options") or {}
        options_key = (arguments.get("method", "highs"), options.get("presolve", True),
                       float(options.get("primal_feasibility_tolerance", 1e-7)),
                       float(options.get("dual_feasibility_tolerance", 1e-7)))
        key = (options_key, *(_array_key(value) for value in (a_ub, b_ub, a_eq, b_eq, bounds)))
        model = self.models.pop(key, None)
        if model is not None:
            self.hits += 1
            _require_ok(model.solver.clearModel())
            model.template.col_cost_ = c
            _require_ok(model.solver.passModel(model.template))
        else:
            data, indices, indptr = _matrix_csc(a_ub, a_eq)
            rhs = np.concatenate((b_ub, b_eq))
            lhs = np.concatenate((np.full_like(b_ub, -np.inf), b_eq))
            lower, upper = bounds.T.copy()
            for array in (rhs, lhs, lower, upper):
                array[array == np.inf] = highs.kHighsInf
                array[array == -np.inf] = -highs.kHighsInf
            size = sum(value.nbytes for value in (a_ub, b_ub, a_eq, b_eq, bounds, data, indices, indptr))
            recyclable = next((key for key, value in self.models.items()
                               if value.options_key == options_key), None)
            if recyclable is not None and (len(self.models) >= 32 or self.bytes + size > 4_194_304):
                previous = self.models.pop(recyclable)
                self.bytes -= previous.bytes
                solver = previous.solver
                _require_ok(solver.clearModel())
            else:
                solver = highs._Highs()
                _require_ok(solver.passOptions(self._options(options_key)))
            lp = highs.HighsLp()
            lp.num_col_, lp.num_row_ = len(c), len(rhs)
            lp.a_matrix_.num_col_, lp.a_matrix_.num_row_ = len(c), len(rhs)
            lp.a_matrix_.format_ = highs.MatrixFormat.kColwise
            lp.col_cost_ = c
            lp.col_lower_, lp.col_upper_ = lower, upper
            lp.row_lower_, lp.row_upper_ = lhs, rhs
            lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = indptr, indices, data
            _require_ok(solver.passModel(lp))
            model = _NativeModel(solver, lp, options_key, size)
            self.bytes += size
        _require_ok(model.solver.clearSolver())
        if model.bytes <= 4_194_304:
            self.models[key] = model
            while len(self.models) > 32 or self.bytes > 4_194_304:
                _, removed = self.models.popitem(last=False)
                self.bytes -= removed.bytes
        else:
            self.bytes -= model.bytes
        _require_ok(model.solver.run())
        return _validated_result(model.solver, problem)


def _validated_result(solver, problem):
    _, _, b_ub, _, b_eq, bounds, _, _ = problem
    native_status = solver.getModelStatus()
    info = solver.getInfo()
    native_message = solver.modelStatusToString(native_status)
    x = fun = slack = con = None
    if native_status == highs.HighsModelStatus.kOptimal:
        solution = solver.getSolution()
        x = np.asarray(solution.col_value)
        fun = info.objective_function_value
        residual = np.concatenate((b_ub, b_eq)) - solution.row_value
        slack, con = residual[:len(b_ub)], residual[len(b_ub):]
    else:
        native_message = (f"model_status is {native_message}; primal_status is "
                          f"{solver.solutionStatusToString(info.primal_solution_status)}")
    status, message = _highs_to_scipy_status_message(native_status, native_message)
    status, message = continuous_check(_check_result, x, fun, status, slack, con, bounds, 1e-9, message)
    return OptimizeResult(x=x, fun=fun, slack=slack, con=con, status=status, message=message,
                          success=status == 0,
                          nit=info.simplex_iteration_count or info.ipm_iteration_count,
                          crossover_nit=info.crossover_iteration_count)
