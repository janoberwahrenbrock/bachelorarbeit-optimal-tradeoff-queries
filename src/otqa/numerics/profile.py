"""Resolved, active method constants; no user policy or inactive modes."""
from copy import deepcopy

GRID_MINIMUM = 0.05
GRID_MAXIMUM = 20.0

_VALUES = {
    "query_generation": {
        "min_grid_value": GRID_MINIMUM, "max_grid_value": GRID_MAXIMUM, "grid_spacing": "log",
        "ratio_query_epsilon": 1e-3, "raw_query_tolerance": 1e-12,
        "dedup_abs_tolerance": 1e-12, "dedup_rel_tolerance": 1e-9,
        "answered_abs_tolerance": 1e-12, "answered_rel_tolerance": 1e-9,
        "grid_close_abs_tolerance": 1e-15, "grid_close_rel_tolerance": 1e-12,
        "answer_order": ["<", "=", ">"],
    },
    "linear_programming": {
        "method": "highs", "primal_feasibility_tolerance": 1e-10,
        "dual_feasibility_tolerance": 1e-10, "primal_validation_tol": 1e-9,
        "presolve_first": True, "retry_without_presolve": True,
        "retry_methods": ["highs-ds", "highs-ipm"], "cold_solve": True,
        "variable_bounds": "explicit_constraints_free_variables",
        "primal_validation_rule": "sqrt_tol_times_10",
    },
    "geometry": {
        "tolerance": 1e-10, "candidate_mode": "ratio_relevant",
        "skip_exact_zero_branches": True, "support_margin_factor": 100.0,
        "support_margin_floor": 1e-8, "equality_residual_factor": 10.0,
        "ratio_terminal_tolerance": 1e-12, "support_tolerance": 1e-10,
        "ratio_batch_elements": 1_048_576, "ratio_batch_pair_factor": 4,
        "containment_relative_tolerance": 1e-8, "snap_relative_tolerance": 1e-5,
        "snap_dedup_tolerance": 1e-10, "halfspace_options": [None, "Q12", "Q12 QJ"],
        "higher_dim_prefix": "Qx", "hull_fallback": "QJ",
    },
    "exact_recovery": {
        "max_lp_variables": 5, "max_active_sets": 20_000,
        "max_explicit_affine_dimension": 2, "decimal_precision": 80,
    },
    "simplex_partition_recovery": {
        "max_goals": 7, "max_constraints": 96, "max_vertices": 1024,
        "max_pair_checks": 200_000, "max_rank_calls": 100_000,
        "max_faces": 30_000, "max_simplices": 100_000,
        "max_operations": 3_000_000, "max_bits": 8192,
        "max_wall_seconds": 45.0,
    },
}


def resolved_numerical_profile() -> dict:
    values = deepcopy(_VALUES)
    numeric_hex = {f"/values/{group}/{key}": value.hex()
                   for group, settings in values.items()
                   for key, value in settings.items() if type(value) is float}
    return {"profile_id": "otqa-exact-v3", "values": values, "numeric_hex": numeric_hex}


def resolved_cache_policy() -> dict:
    return {"policy_id": "bounded_v1", "owner": "solver_and_worker_session",
            "state_entries": 16, "planning_entries": 16, "volume_entries": 32768,
            "vertex_entries": 32768, "vertex_bytes": 67_108_864,
            "affine_entries": 4096, "affine_bytes": 8_388_608,
            "highs_models": 32, "highs_model_bytes": 4_194_304, "highs_options": 32}


def actual_backend_capabilities() -> dict:
    """Inspect actual loaded bindings; call only after numerical bootstrap."""
    from .native import AVAILABLE
    from .validation import SOURCE_VERIFIED
    return {"scipy_highs": True, "scipy_qhull": True, "reusable_highs": bool(AVAILABLE),
            "continuous_validation_fastpath": bool(AVAILABLE and SOURCE_VERIFIED)}
