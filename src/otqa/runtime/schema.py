"""One offline registry for native wire contracts.

This is the product's schema authority. Domain objects deliberately do not depend
on these definitions; document adapters validate and project at their boundary.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from .codec import DocumentError

BASE = "urn:otqa:v1:"
DIALECT = "https://json-schema.org/draft/2020-12/schema"


def object_of(fields: dict, *, optional: tuple[str, ...] = ()) -> dict:
    return {"type": "object", "properties": fields,
            "required": [key for key in fields if key not in optional],
            "additionalProperties": False}


def array_of(item: dict, minimum: int = 0, *, unique: bool = False) -> dict:
    result = {"type": "array", "items": item, "minItems": minimum}
    if unique:
        result["uniqueItems"] = True
    return result


def integer(minimum: int = 0, maximum: int | None = None) -> dict:
    value = {"type": "integer", "minimum": minimum}
    if maximum is not None:
        value["maximum"] = maximum
    return value


def number(minimum: float | None = None, maximum: float | None = None, *, positive=False) -> dict:
    value = {"type": "number"}
    if minimum is not None:
        value["minimum"] = minimum
    if maximum is not None:
        value["maximum"] = maximum
    if positive:
        value["exclusiveMinimum"] = 0
    return value


def choices(*values: str) -> dict:
    return {"enum": list(values)}


def nullable(value: dict) -> dict:
    return {"anyOf": [value, {"type": "null"}]}


def reference(name: str) -> dict:
    return {"$ref": BASE + "common#/$defs/" + name}


TEXT = {"type": "string", "minLength": 1}
BOOL = {"type": "boolean"}
ID = {"type": "string", "pattern": r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"}
UUID = {"type": "string", "format": "uuid"}
UTC = {"type": "string", "format": "date-time", "pattern": "Z$"}
HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
PATH = {"type": "string", "minLength": 1,
        "pattern": r"^(?!/)(?!.*(?:^|/)\.{1,2}(?:/|$))(?!.*[\\:\x00-\x1f\x7f])(?!.*//).+[^/]$|^[A-Za-z0-9_-]$"}
HEX = {"type": "string", "pattern": r"^-?0x[0-9a-f]+\.[0-9a-f]+p[+-][0-9]+$"}
HEXMAP = {"type": "object", "additionalProperties": HEX}
FREE = {"type": "object"}
VERSION = {"const": 1}
STATUSES = choices("pending", "launching", "running", "completed", "failed", "interrupted")
REASONS = choices("exact_single_candidate", "volume_confidence", "no_query", "max_questions")
PHASE = choices("started", "analyzing", "planning", "awaiting_answer", "answer_committed", "completed", "failed", "interrupted")


def definitions() -> tuple[dict, dict]:
    """Construct common types and all document variants without filesystem work."""
    d: dict[str, dict] = {}
    docs: dict[str, dict] = {}
    r = reference
    obj = object_of
    arr = array_of
    d["FileRef"] = obj({"path": PATH, "sha256": HASH})
    d["ProjectBinding"] = obj({"project_id": UUID, "relative_root": {"allOf": [PATH, {"pattern": "^runs/.+"}]}})
    d["Query"] = obj({"goal_index_a": integer(), "goal_index_b": integer(), "value": number(0)})
    d["AnsweredQuery"] = obj({**d["Query"]["properties"], "answer": choices("<", "=", ">")})
    d["QueryCounts"] = obj({name: integer() for name in ("initial_answers", "dispatched_new", "answered_new", "answered_total")})
    d["Source"] = obj({"inventory_format": {"const": "otqa-source-v1"}, "version": TEXT,
                        "git_commit": nullable({"type": "string", "pattern": "^[0-9a-f]{40}$"}),
                        "dirty": BOOL, "source_sha256": HASH})
    d["ProcessIdentity"] = obj({"pid": integer(1), "hostname": TEXT,
        "identity_method": choices("linux_proc", "owned_child"), "boot_id": nullable(TEXT),
        "start_ticks": nullable(integer()), "pgid": nullable(integer(1)), "sid": nullable(integer(1)), "owner_token": ID})
    d["Error"] = obj({"code": choices("invalid_input", "invalid_answer", "infeasible_state", "numerical_failure",
        "planning_invariant", "answer_provider", "observer", "worker_failure", "artifact_corruption", "persistence_failure",
        "context_unavailable", "oracle_consistency", "unknown"), "type": TEXT, "message": TEXT,
        "traceback": nullable(TEXT), "stage": choices("input", "provider", "observer", "numerics", "planning", "worker", "persistence", "controller"), "context": FREE})
    d["Interruption"] = obj({"reason": choices("user_cancel", "timeout", "controller_lost"), "message": TEXT})
    d["Quality"] = obj({"status": choices("correct", "incorrect", "unknown", "not_selected"),
        "audit_status": choices("passed", "failed", "not_available"), "true_winner_ids": arr(ID, unique=True),
        "regret_fraction": nullable({"type": "string", "pattern": r"^-?[0-9]+(?:/[1-9][0-9]*)?$"}), "findings": arr(TEXT)})
    time_fields = ("case_elapsed_seconds", "api_call_wall_seconds", "partial_api_elapsed_seconds", "state_analysis_wall_seconds",
        "planning_wall_seconds", "answer_wait_wall_seconds", "recorder_wall_seconds", "observer_wall_seconds", "persistence_in_call_wall_seconds",
        "worker_startup_wall_seconds", "worker_shutdown_wall_seconds", "unattributed_wall_seconds", "worker_cpu_seconds")
    d["Timings"] = obj({**{key: nullable(number(0)) for key in time_fields}, "scope_version": VERSION, "complete_api_measurement": BOOL})
    shares = {"type": "object", "propertyNames": ID, "additionalProperties": number(0, 1)}
    volumes = {"type": "object", "propertyNames": ID, "additionalProperties": number(0)}
    d["State"] = obj({"state_index": integer(), "last_answer_query_id": nullable(ID), "candidate_ids": arr(ID, unique=True),
        "candidate_volumes": nullable(volumes), "candidate_volume_shares": nullable(shares)})
    d["FixedScore"] = obj({"kind": {"const": "fixed"}, "expected_terminal_candidates": number(0), "expected_terminal_loss": number(0),
        "lexicographic_expected_values": arr(number(), 1), "expected_queries": number(0)}, optional=("expected_queries",))
    d["EfficiencyScore"] = obj({"kind": {"const": "reduction_per_query"}, "expected_terminal_candidates": number(0), "expected_terminal_loss": number(0),
        "expected_queries": number(positive=True), "gain": number(), "rate": number()})
    d["Score"] = {"oneOf": [r("FixedScore"), r("EfficiencyScore")]}
    d["PlanSummary"] = obj({"horizon": integer(1, 3), "query": r("Query"), "score": r("Score"),
        "answer_probabilities": obj({answer: number(0, 1) for answer in ("<", "=", ">")})})
    d["HorizonSummary"] = obj({"horizon": integer(1, 3), "status": choices("available", "no_query"), "plan": nullable(r("PlanSummary"))})
    d["PlanTree"] = obj({"node_id": ID, "candidate_count": integer(), "stop_reason": nullable(choices("exact_single_candidate", "volume_confidence")),
        "maximum_volume_share": nullable(number(0, 1)), "query": nullable(r("Query")), "expected_terminal_candidates": number(0),
        "expected_terminal_loss": number(0), "expected_queries": number(0),
        "branches": arr(obj({"answer": choices("<", "=", ">"), "probability": number(0, 1), "child": nullable(r("PlanTree"))}))}, optional=("expected_queries",))
    d["Planning"] = obj({"selected": r("PlanSummary"), "horizons": arr(r("HorizonSummary"), 1), "planning_stop_aware": BOOL, "plan_tree": nullable(r("PlanTree"))})
    d["QueryRecord"] = obj({"query_id": ID, "query": r("Query"), "answer": choices("<", "=", ">"), "planning": r("Planning"),
                            "state_before_index": integer(), "state_after_index": integer()})
    d["SolverResult"] = obj({"solved": BOOL, "exactly_solved": BOOL, "termination_reason": REASONS, "selected_candidate_id": nullable(ID),
        "selected_candidate_volume": nullable(number(0)), "selected_candidate_volume_share": nullable(number(0, 1)),
        "final_state": r("State"), "query_records": arr(r("QueryRecord")), "answered_queries": arr(r("AnsweredQuery"))})
    stopping = {"oneOf": [obj({"rule": {"const": "single_candidate"}}), obj({"rule": {"const": "volume_confidence"}, "threshold": number(maximum=1, positive=True)})]}
    d["AlgorithmPolicy"] = obj({"query_strategy": choices("fixed", "reduction_per_query"), "depth": integer(1, 3),
        "higher_depth_query_source": choices("grid", "both"), "grid_size": integer(1), "planning_evaluation": choices("candidate_count", "stop_aware"), "stopping": stopping})
    d["QueryBudget"] = obj({"max_queries": nullable(integer(1))})
    d["ExecutionOptions"] = obj({"workers": integer(1), "start_method": {"const": "forkserver"}, "native_threads": integer(1),
        "case_timeout_seconds": nullable(number(positive=True)), "cache_policy_id": {"const": "bounded_v1"}})
    d["RecordingOptions"] = obj({"durability": {"const": "per_answer"}, "trace_level": choices("standard", "full"), "profile": BOOL, "telemetry_failure_policy": choices("continue", "abort")})
    cache_fields = ("state_entries", "planning_entries", "volume_entries", "vertex_entries", "vertex_bytes", "affine_entries", "affine_bytes", "highs_models", "highs_model_bytes", "highs_options")
    d["CachePolicy"] = obj({"policy_id": {"const": "bounded_v1"}, "owner": {"const": "solver_and_worker_session"}, **{key: integer(1) for key in cache_fields}})
    d["NumericalProfile"] = obj({"profile_id": ID, "values": r("ActiveNumerics"), "numeric_hex": HEXMAP})
    d["ActiveNumerics"] = _numerics()
    docs["project"] = obj({"schema_version": VERSION, "project_kind": {"const": "otqa_project"}, "project_id": UUID})
    docs["source_inventory"] = obj({"schema_version": VERSION, "inventory_format": {"const": "otqa-source-v1"},
        "files": arr(obj({"path": {"allOf": [PATH, {"pattern": r"^otqa/(?:.+\.py|schemas/.+\.json)$"}]}, "bytes": integer(), "sha256": HASH}), 1)})
    docs["source_build_provenance"] = obj({"schema_version": VERSION, "source": r("Source"), "inventory_sha256": HASH})
    docs["problem"] = obj({"schema_version": VERSION, "problem_id": ID, "alternative_ids": arr(ID, 1, unique=True),
        "objective_ids": arr(ID, 1, unique=True), "alternatives": arr(arr(number(0, 1), 1), 1)})
    docs["oracle"] = obj({"schema_version": VERSION, "problem_id": ID, "target_weights": arr(number(0), 1)})
    docs["answer_history"] = obj({"schema_version": VERSION, "problem_id": ID, "answers": arr(r("AnsweredQuery"))})
    docs["config"] = obj({"schema_version": VERSION, "configuration_id": ID, "algorithm": r("AlgorithmPolicy"), "budget": r("QueryBudget"), "execution": r("ExecutionOptions"), "recording": r("RecordingOptions")})
    docs["dataset"] = obj({"schema_version": VERSION, "dataset_id": ID, "generator": nullable(FREE), "cases": arr(obj({"case_id": ID, "problem": r("FileRef"), "oracle": r("FileRef")}), 1)})
    docs["suite"] = obj({"schema_version": VERSION, "suite_id": ID, "dataset": r("FileRef"),
        "configurations": arr(obj({"configuration_id": ID, "path": PATH, "sha256": HASH}), 1),
        "selection": arr(obj({"configuration_id": ID, "case_ids": arr(ID, 1, unique=True)}), 1), "repetitions": integer(1),
        "execution": obj({"max_concurrent_cases": {"const": 1}, "job_order": {"const": "case_repetition_config_rotated"}})})
    docs["execution_profile"] = obj({"schema_version": VERSION, "profile_id": ID, "platform_family": choices("linux", "macos"), "python_version": TEXT,
        "packages": {"type": "object", "additionalProperties": TEXT}, "backend_capabilities": FREE, "environment_lock": r("FileRef"),
        "certification": obj({"status": choices("validated", "illustrative_only", "qualifying"), "evidence": nullable(r("FileRef"))})})
    _execution_documents(d, docs)
    _analysis_documents(d, docs)
    return d, docs


def _numerics() -> dict:
    obj = object_of
    pos = number(positive=True)
    zero = number(0)
    query_fields = {key: zero for key in ("raw_query_tolerance", "dedup_abs_tolerance", "dedup_rel_tolerance", "answered_abs_tolerance", "answered_rel_tolerance", "grid_close_abs_tolerance", "grid_close_rel_tolerance")}
    query_fields.update(min_grid_value=pos, max_grid_value=pos, grid_spacing={"const": "log"}, ratio_query_epsilon=pos,
        answer_order=array_of(choices("<", "=", ">"), 3, unique=True))
    lp = {key: pos for key in ("primal_feasibility_tolerance", "dual_feasibility_tolerance", "primal_validation_tol")}
    lp.update(method={"const": "highs"}, presolve_first=BOOL, retry_without_presolve=BOOL,
        retry_methods=array_of(choices("highs-ds", "highs-ipm"), 1, unique=True), cold_solve={"const": True},
        variable_bounds={"const": "explicit_constraints_free_variables"}, primal_validation_rule={"const": "sqrt_tol_times_10"})
    geo = {key: pos for key in ("tolerance", "support_margin_factor", "support_tolerance", "support_margin_floor", "equality_residual_factor", "containment_relative_tolerance", "snap_relative_tolerance", "snap_dedup_tolerance")}
    geo.update(candidate_mode={"const": "ratio_relevant"}, skip_exact_zero_branches={"const": True}, ratio_terminal_tolerance=zero,
        ratio_batch_elements=integer(1), ratio_batch_pair_factor=integer(1), halfspace_options=array_of(nullable(TEXT), 1), higher_dim_prefix=TEXT, hull_fallback=TEXT)
    recovery = {key: integer(1) for key in ("max_lp_variables", "max_active_sets", "decimal_precision")}
    recovery["max_explicit_affine_dimension"] = integer()
    return obj({"query_generation": obj(query_fields), "linear_programming": obj(lp), "geometry": obj(geo), "exact_recovery": obj(recovery)})


def _execution_documents(d: dict, docs: dict) -> None:
    obj, arr, r = object_of, array_of, reference
    scope = choices("sdk", "standalone", "series_linux_recovery")
    check = choices("installation", "backend_conformance", "numerical_conformance", "sdk_lifecycle", "standalone_io", "linux_recovery")
    passed = choices("passed", "failed", "inconclusive")
    docs["certification"] = obj({"schema_version": VERSION, "certification_id": ID, "created_at_utc": UTC, "purpose": {"const": "native_runtime"},
        "source": r("Source"), "profile_projection_sha256": HASH, "environment_lock": r("FileRef"), "numerical_profile_id": ID,
        "numerical_values_sha256": HASH, "cache_policy_id": ID, "scopes": arr(scope, 1, unique=True),
        "checks": arr(obj({"check_id": check, "scope": scope, "status": passed, "evidence": r("FileRef")}), 1), "status": choices("passed", "failed"), "illustrative_only": BOOL})
    docs["certification_check_evidence"] = obj({"schema_version": VERSION, "purpose": {"const": "native_runtime"}, "inventory_format": {"const": "otqa-source-v1"},
        "check_id": check, "scope": scope, "source_sha256": HASH, "profile_projection_sha256": HASH, "numerical_values_sha256": HASH, "cache_policy_id": ID,
        "method": TEXT, "status": passed, "raw_reports": arr(r("FileRef"), 1), "illustrative_only": BOOL})
    docs["materialization_receipt"] = obj({"schema_version": VERSION, "materialization_id": UUID, "created_at_utc": UTC,
        "entrypoints": {"type": "object", "propertyNames": ID, "additionalProperties": r("FileRef"), "minProperties": 1},
        "entries": arr(obj({"document_kind": choices("problem", "oracle", "answer_history", "config", "dataset", "suite", "execution_profile", "certification", "certification_check_evidence", "blob"),
            "source_relative_path": PATH, "original": r("FileRef"), "materialized": r("FileRef"), "transformation": choices("byte_copy", "reference_rewrite"),
            "semantic_sha256": HASH, "reference_map": arr(obj({"json_pointer": {"type": "string"}, "source_path": PATH, "materialized_path": PATH}))}), 1)})
    ids = {"schema_version": VERSION, "run_id": UUID, "attempt_id": ID}
    docs["launch_intent"] = obj({**ids, "series_id": nullable(UUID), "job_id": nullable(ID), "problem_id": ID, "configuration_id": ID,
        "created_at_utc": UTC, "owner_token": ID, "nonce": ID, "controller": r("ProcessIdentity"), "materialization_receipt": r("FileRef")})
    docs["child_registration"] = obj({**ids, "created_at_utc": UTC, "intent": r("FileRef"), "nonce": ID, "process": r("ProcessIdentity")})
    docs["start_grant"] = obj({**ids, "created_at_utc": UTC, "intent": r("FileRef"), "registration": r("FileRef"), "nonce": ID, "process": r("ProcessIdentity")})
    docs["manifest"] = obj({**ids, "series_id": nullable(UUID), "job_id": nullable(ID), "problem_id": ID, "configuration_id": ID,
        "execution_kind": choices("fresh", "continuation", "replay"), "answer_source": choices("interactive", "simulated", "replay"), "created_at_utc": UTC,
        "source": r("Source"), "source_inventory": r("FileRef"), "project_binding": r("ProjectBinding"), "run_purpose": choices("production", "qualification"),
        "materialization_receipt": r("FileRef"), "launch_intent": r("FileRef"), "inputs": obj({"problem": r("FileRef"), "configuration": r("FileRef"),
            "oracle": nullable(r("FileRef")), "initial_answers": nullable(r("FileRef")), "replay_answers": nullable(r("FileRef"))}),
        "mathematical_input_sha256": HASH, "effective_algorithm": r("AlgorithmPolicy"), "effective_budget": r("QueryBudget"),
        "effective_execution": r("ExecutionOptions"), "effective_recording": r("RecordingOptions"), "execution_profile": r("FileRef"),
        "numerical_profile": r("NumericalProfile"), "resolved_cache_policy": r("CachePolicy"), "environment": obj({"hostname": TEXT, "platform_family": choices("linux", "macos"),
            "platform": TEXT, "python": TEXT, "packages": {"type": "object", "additionalProperties": TEXT}, "cpu_model": nullable(TEXT), "physical_cores": nullable(integer(1)),
            "logical_cpus": nullable(integer(1)), "native_thread_environment": {"type": "object", "additionalProperties": TEXT}, "backend_capabilities": FREE}), "process": r("ProcessIdentity")})
    payloads = {"run_started": obj({"manifest_sha256": HASH}), "state_analyzed": r("State"),
        "query_planned": obj({"state_before_index": integer(), "planning": r("Planning")}), "query_dispatched": obj({"query": r("Query"), "dispatched_new": integer(1)}),
        "answer_received": obj({"query": r("Query"), "answer": choices("<", "=", ">"), "answered_new": integer(1), "answered_total": integer(1)}), "query_completed": r("QueryRecord"),
        "run_finished": obj({"termination_reason": REASONS, "solved": BOOL, "query_counts": r("QueryCounts")}),
        "run_failed": obj({"error": r("Error"), "query_counts": r("QueryCounts")}), "run_interrupted": obj({"interruption": r("Interruption"), "query_counts": r("QueryCounts")})}
    variants = []
    for name, payload in payloads.items():
        variants.append(obj({**ids, "sequence": integer(1), "occurred_at_utc": UTC, "monotonic_ns": integer(), "event_type": {"const": name},
                             "query_id": nullable(ID), "payload": payload, "numeric_hex": HEXMAP}))
    docs["event"] = {"oneOf": variants}
    d["JournalProof"] = obj({"path": PATH, "sha256": HASH, "bytes": integer(), "valid_prefix_bytes": integer(), "valid_prefix_sha256": HASH,
        "last_good_sequence": integer(), "trailing_partial_line": BOOL, "uncommitted_suffix_bytes": integer()})
    docs["result"] = obj({**ids, "problem_id": ID, "configuration_id": ID, "execution_status": choices("completed", "failed", "interrupted"),
        "execution_stage": choices("bootstrap", "solver"), "finalized_by": choices("case_process", "controller"), "started_at_utc": UTC, "finished_at_utc": UTC,
        "query_counts": r("QueryCounts"), "timings": r("Timings"), "solver_result": nullable(r("SolverResult")), "quality": r("Quality"),
        "error": nullable(r("Error")), "interruption": nullable(r("Interruption")), "telemetry_errors": arr(r("Error")), "journal": nullable(r("JournalProof")), "numeric_hex": HEXMAP})
    d["Job"] = obj({"job_id": ID, "case_id": ID, "problem_id": ID, "configuration_id": ID, "repetition_index": integer(),
                    "problem": r("FileRef"), "oracle": r("FileRef"), "configuration": r("FileRef")})
    docs["series_plan"] = obj({"schema_version": VERSION, "series_id": UUID, "suite_id": ID, "created_at_utc": UTC, "source": r("Source"), "project_binding": r("ProjectBinding"),
        "execution_profile": r("FileRef"), "suite": r("FileRef"), "dataset": r("FileRef"), "frozen_files": {"type": "object", "propertyNames": PATH, "additionalProperties": HASH},
        "jobs": arr(r("Job"), 1), "run_purpose": choices("production", "qualification"), "materialization_receipt": r("FileRef")})
    d["AttemptState"] = obj({"attempt_id": ID, "run_id": UUID, "directory": {"anyOf": [{"const": "."}, PATH]}, "execution_status": choices("launching", "running", "completed", "failed", "interrupted"),
        "launch_intent": r("FileRef"), "child_registration": nullable(r("FileRef")), "start_grant": nullable(r("FileRef")), "process": nullable(r("ProcessIdentity")),
        "result": nullable(r("FileRef")), "controller_elapsed_seconds": nullable(number(0))})
    docs["series_state"] = obj({"schema_version": VERSION, "series_id": UUID, "plan_sha256": HASH, "revision": integer(1), "updated_at_utc": UTC,
        "status": choices("planned", "running", "interrupted", "completed", "completed_with_failures"), "controller": nullable(r("ProcessIdentity")), "active_job_id": nullable(ID),
        "jobs": arr(obj({"job_id": ID, "status": STATUSES, "attempts": arr(r("AttemptState"))}), 1)})
    docs["progress"] = obj({**ids, "updated_at_utc": UTC, "last_good_sequence": integer(), "valid_prefix_bytes": integer(), "valid_prefix_sha256": HASH,
        "query_counts": r("QueryCounts"), "partial_api_elapsed_seconds": nullable(number(0)), "query_phase": PHASE, "active_query_id": nullable(ID), "process": r("ProcessIdentity")})
    docs["partial_snapshot"] = obj({**ids, "snapshot_id": UUID, "created_at_utc": UTC, "manifest": r("FileRef"), "journal_path": PATH,
        "valid_prefix_bytes": integer(), "valid_prefix_sha256": HASH, "last_good_sequence": integer(), "query_counts": r("QueryCounts"), "query_phase": PHASE,
        "active_query_id": nullable(ID), "partial_api_elapsed_seconds": nullable(number(0))})


def _analysis_documents(d: dict, docs: dict) -> None:
    obj, arr, r = object_of, array_of, reference
    docs["audit"] = obj({"schema_version": VERSION, "audit_id": UUID, "series_id": UUID, "created_at_utc": UTC, "auditor": r("Source"), "plan": r("FileRef"), "state": r("FileRef"),
        "prefix_snapshots": arr(r("FileRef")), "status": choices("passed", "failed", "partial"), "checks": arr(obj({"check_id": ID, "status": choices("passed", "failed", "not_applicable"),
            "message": TEXT, "artifact": nullable(r("FileRef")), "json_pointer": nullable({"type": "string"})}), 1)})
    d["Distribution"] = obj({"n": integer(), **{key: nullable(number(0)) for key in ("total", "mean", "median", "minimum", "maximum", "p90")}})
    d["SummaryRow"] = obj({"job_id": ID, "case_id": ID, "configuration_id": ID, "repetition_index": integer(), "objective_count": integer(1), "alternative_count": integer(1),
        "status": STATUSES, "accepted_attempt_id": nullable(ID), "termination_reason": nullable(REASONS), "solved": nullable(BOOL), "selected_candidate_id": nullable(ID),
        "quality_status": choices("correct", "incorrect", "unknown", "not_selected"), "query_counts": nullable(r("QueryCounts")), "api_call_wall_seconds": nullable(number(0)), "attempt_results": arr(r("FileRef"))})
    counts = ("planned_jobs", "unique_cases", "completed_native", "solved", "singleton_stops", "confidence_stops", "no_query", "query_cap", "correct", "incorrect", "unknown_quality", "failed", "interrupted", "pending", "launching", "running", "total_attempts", "unknown_controller_attempt_times")
    distributions = ("solution_time", "correct_solution_time", "completed_call_time", "controller_attempt_time", "failed_api_call_time", "answered_new_solved", "answered_new_correct", "answered_new_completed")
    d["SummaryGroup"] = obj({"configuration_id": ID, "objective_count": integer(1), "alternative_count": integer(1), **{key: integer() for key in counts},
        **{key: r("Distribution") for key in distributions}, **{key: arr(ID, unique=True) for key in ("solution_sample_job_ids", "correct_sample_job_ids", "completed_sample_job_ids")}})
    docs["summary"] = obj({"schema_version": VERSION, "series_id": UUID, "generated_at_utc": UTC, "scope": choices("complete", "partial"), "basis": {"const": "verified_raw_attempts"},
        "plan": r("FileRef"), "state": r("FileRef"), "audit": r("FileRef"), "prefix_snapshots": arr(r("FileRef")), "rows": arr(r("SummaryRow"), 1), "groups": arr(r("SummaryGroup"), 1)})
    docs["profile"] = obj({"schema_version": VERSION, "run_id": UUID, "attempt_id": ID, "manifest": r("FileRef"), "collector": choices("phase_ledger", "cprofile", "worker_cprofile"),
        "metrics": arr(obj({"metric_id": ID, "scope": choices("wall", "cpu", "counter"), "aggregation": choices("exclusive", "inclusive", "count"), "value": number(0), "unit": choices("seconds", "count")}), 1), "raw_reports": arr(r("FileRef"))})
    docs["archive_inventory"] = obj({"schema_version": VERSION, "series_id": UUID, "created_at_utc": UTC, "inventory_sha256": HASH,
        "files": arr(obj({"path": PATH, "bytes": integer(), "sha256": HASH}), 1)})


@lru_cache(maxsize=1)
def registry_and_validators():
    from jsonschema import Draft202012Validator, FormatChecker, validators
    from referencing import Registry, Resource
    defs, docs = definitions()
    checker = Draft202012Validator.TYPE_CHECKER.redefine("integer", lambda checker, value: type(value) is int)
    checker = checker.redefine("number", lambda checker, value: type(value) in (int, float) and _finite(value))
    strict = validators.extend(Draft202012Validator, type_checker=checker)
    common = {"$schema": DIALECT, "$id": BASE + "common", "$defs": defs}
    registry = Registry().with_resource(BASE + "common", Resource.from_contents(common))
    return {kind: strict({"$schema": DIALECT, "$id": BASE + kind, **schema}, registry=registry, format_checker=FormatChecker()) for kind, schema in docs.items()}


def _finite(value: Any) -> bool:
    import math
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def validate(kind: str, document: Any) -> Any:
    try:
        validator = registry_and_validators()[kind]
    except KeyError as exc:
        raise DocumentError(f"Unknown native document kind: {kind}") from exc
    errors = sorted(validator.iter_errors(document), key=lambda error: str(list(error.path)))
    if errors:
        first = errors[0]
        raise DocumentError(f"{kind} at /{'/'.join(map(str, first.path))}: {first.message}")
    return document


def write_schema_resources(directory) -> tuple[str, ...]:
    """Build-time resource generation; runtime validation performs no writes."""
    from pathlib import Path
    from .codec import encode
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    defs, docs = definitions()
    resources = {"common": {"$schema": DIALECT, "$id": BASE + "common", "$defs": defs}}
    resources.update({kind: {"$schema": DIALECT, "$id": BASE + kind, **schema} for kind, schema in docs.items()})
    for kind, document in resources.items():
        (root / f"{kind}.schema.json").write_bytes(encode(document))
    return tuple(resources)
