"""Method-specific readers for native qualification raw reports.

These records qualify runtime mechanics and analytical controls. They contain
no migration baseline or performance acceptance claims.
"""
from __future__ import annotations

from .codec import DocumentError, decode

METHOD_CASES = {
    "installation": ("installed_distribution", "external_cwd_import", "console_help", "light_import", "source_inventory", "offline_schemas", "dependency_versions"),
    "backend_conformance": ("lp_optimal", "lp_infeasible", "lp_unbounded", "lp_failure_injection", "qhull_full_dimensional", "qhull_degenerate", "capabilities"),
    "numerical_conformance": ("simplex_volume", "symmetric_response_probabilities", "equality_dimension", "binary64_input_identity"),
    "sdk_lifecycle": ("singleton_stop", "answered_query_solve", "initial_history", "provider_failure", "recorder_failure", "observer_failure", "reentrant_sessions", "owned_worker_pool"),
    "standalone_io": ("isolated_case", "durable_launch_chain", "durable_journal_counts", "provider_failure_counts", "pre_release_eof", "cursor_publication_failure", "project_boundary", "series_audit_export"),
    "linux_recovery": ("live_group_blocks_resume", "dead_group_fresh_retry", "unregistered_eof", "uncertain_start_blocks_resume", "all_attempts_retained"),
}


def verify_raw_report(data: bytes, evidence: dict) -> dict:
    report = decode(data)
    required = {"schema_version", "purpose", "method", "check_id", "scope", "inventory_format", "source_sha256", "profile_projection_sha256",
                "numerical_values_sha256", "cache_policy_id", "started_at_utc", "finished_at_utc", "observations", "status", "harness_sha256"}
    if not isinstance(report, dict) or set(report) != required or type(report["schema_version"]) is not int or report["schema_version"] != 1:
        raise DocumentError("Unknown or incomplete native qualification raw report")
    for field in ("purpose", "method", "check_id", "scope", "inventory_format", "source_sha256", "profile_projection_sha256", "numerical_values_sha256", "cache_policy_id"):
        if report[field] != evidence[field]:
            raise DocumentError(f"Raw report {field} differs from its check evidence")
    if report["status"] != "passed" or report["purpose"] != "native_runtime":
        raise DocumentError("Raw report did not pass native runtime qualification")
    cases = METHOD_CASES[report["check_id"]]
    observations = report["observations"]
    if not isinstance(observations, list) or [item.get("case_id") for item in observations if isinstance(item, dict)] != list(cases):
        raise DocumentError("Method-specific qualification observations are missing, duplicated or reordered")
    for item in observations:
        if set(item) != {"case_id", "expected", "observed", "passed", "details"} or item["expected"] is not True or item["observed"] is not True or item["passed"] is not True:
            raise DocumentError("A native qualification control did not meet its explicit pass rule")
        if not isinstance(item["details"], dict) or not item["details"]:
            raise DocumentError("Qualification control is missing concrete observations")
    # Reuse the format checker for UTC/hash grammar without a permissive parser.
    from jsonschema import Draft202012Validator, FormatChecker
    validator = Draft202012Validator({"type": "object", "properties": {
        "started_at_utc": {"type": "string", "format": "date-time", "pattern": "Z$"},
        "finished_at_utc": {"type": "string", "format": "date-time", "pattern": "Z$"},
        "harness_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}}}, format_checker=FormatChecker())
    if errors := list(validator.iter_errors(report)):
        raise DocumentError("Malformed raw report timestamp or harness digest: " + errors[0].message)
    return report
