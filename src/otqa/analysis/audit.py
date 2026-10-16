"""Independent artifact/answer audit with one immutable state/prefix snapshot."""
from __future__ import annotations

import copy
from pathlib import Path
from uuid import UUID, uuid4

from otqa.runtime.codec import DocumentError, canonical_digest, digest, float_projection, read_json, utc_now
from otqa.runtime.documents import _at, file_ref, load_document, references, resolve_ref, typed_projection
from otqa.runtime.project import verify_binding
from otqa.runtime.source import loaded_source
from otqa.runtime.storage import create_directory, publish_json
from otqa.runtime.validation import journal_policy, verify_result

from .journal import verify_cursor, verify_prefix
from .quality import evaluate_quality


def report_directory(series_root: Path, output_path: Path) -> Path:
    root, output = Path(series_root).absolute(), Path(output_path).absolute()
    try:
        relative = output.relative_to(root)
    except ValueError as exc:
        raise DocumentError("Native reports must be inside their own series") from exc
    if len(relative.parts) != 3 or relative.parts[0] != "reports" or relative.parts[2] != "audit.json":
        raise DocumentError("Audit path must be SeriesRoot/reports/<UUID>/audit.json")
    try:
        UUID(relative.parts[1])
    except ValueError as exc:
        raise DocumentError("Report directory ID must be a UUID") from exc
    return output.parent


def verify_materialization(root: Path, receipt: dict) -> None:
    entries = receipt["entries"]
    by_source = {entry["source_relative_path"]: entry for entry in entries}
    if len(by_source) != len(entries):
        raise DocumentError("Duplicate source artifact in materialization receipt")
    for entry in entries:
        original = resolve_ref(root, entry["original"])
        native = resolve_ref(root, entry["materialized"])
        if entry["original"]["path"] != "provenance/original/" + entry["source_relative_path"]:
            raise DocumentError("Original materialization namespace differs")
        kind = entry["document_kind"]
        if kind == "blob":
            if original.read_bytes() != native.read_bytes() or digest(original.read_bytes()) != entry["semantic_sha256"]:
                raise DocumentError("Blob materialization changed its bytes")
            continue
        original_doc = load_document(kind, original, reference_root=root)
        native_doc = load_document(kind, native, reference_root=root)
        expected = copy.deepcopy(original_doc)
        projection = typed_projection(kind, original_doc)
        expected_map = []
        for pointer, _, old_ref in references(kind, original_doc):
            source_path = old_ref["path"]
            if source_path not in by_source or by_source[source_path]["original"]["sha256"] != old_ref["sha256"]:
                raise DocumentError("Materialization reference has no original artifact binding")
            mapped = by_source[source_path]["materialized"]
            _at(expected, pointer).update(mapped)
            semantic = _at(projection, pointer)
            semantic.pop("path")
            semantic.pop("sha256")
            semantic["source_artifact_sha256"] = old_ref["sha256"]
            expected_map.append({"json_pointer": pointer, "source_path": source_path, "materialized_path": mapped["path"]})
        if native_doc != expected or expected_map != entry["reference_map"]:
            raise DocumentError("Materialization changed values or undeclared reference positions")
        if canonical_digest(float_projection(projection)) != entry["semantic_sha256"]:
            raise DocumentError("Materialization semantic identity differs")
        if entry["transformation"] == "byte_copy" and original.read_bytes() != native.read_bytes():
            raise DocumentError("Mathematical input was not copied byte-identically")
    for ref in receipt["entrypoints"].values():
        resolve_ref(root, ref)
        if ref not in [entry["materialized"] for entry in entries]:
            raise DocumentError("Materialization entrypoint is absent from its mapping")


def capture_prefix(root: Path, attempt: dict, destination: Path, *, context) -> dict | None:
    directory = root / attempt["directory"]
    progress_path = directory / "progress.json"
    if not progress_path.exists():
        return None
    cursor = load_document("progress", progress_path, reference_root=root)
    manifest_path = directory / "manifest.json"
    manifest = load_document("manifest", manifest_path, reference_root=root)
    if manifest["project_binding"] != context.binding(root):
        raise DocumentError("Live manifest project binding differs from its enclosing series")
    if cursor["run_id"] != attempt["run_id"] or cursor["attempt_id"] != attempt["attempt_id"] or cursor["process"] != manifest["process"]:
        raise DocumentError("Live cursor identity/process binding differs")
    data = (directory / "events.jsonl").read_bytes()
    verified = verify_cursor(data, cursor, **journal_policy(manifest, root, manifest_path))
    if verified["query_counts"] != cursor["query_counts"] or verified["run_id"] != attempt["run_id"]:
        raise DocumentError("Live cursor counts do not match its exact journal prefix")
    snapshot = {"schema_version": cursor["schema_version"], "snapshot_id": str(uuid4()), "created_at_utc": utc_now(), "run_id": cursor["run_id"], "attempt_id": cursor["attempt_id"],
        "manifest": file_ref(manifest_path, root), "journal_path": (directory / "events.jsonl").relative_to(root).as_posix(),
        **{key: cursor[key] for key in ("valid_prefix_bytes", "valid_prefix_sha256", "last_good_sequence", "query_counts", "query_phase", "active_query_id", "partial_api_elapsed_seconds")}}
    if cursor['schema_version'] == 2:
        snapshot['execution_cursor'] = cursor['execution_cursor']
    publish_json(context, destination, snapshot, kind="partial_snapshot")
    return file_ref(destination, root)


def audit_series(request, *, _allow_qualification=False):
    from otqa.application_types import AuditOutcome
    root, context = Path(request.series_dir).absolute(), request.context
    context.binding(root)
    directory = report_directory(root, request.output_path)
    context.relative_output(directory)
    if directory.exists():
        raise DocumentError("Report destination already exists")
    plan = load_document("series_plan", root / "plan.json", reference_root=root)
    verify_binding(context, root, plan["project_binding"])
    if plan["run_purpose"] != "production" and not _allow_qualification:
        raise DocumentError("Public audits accept production plans only")
    # Atomic state read happens once, before any traversal of its referenced data.
    state = load_document("series_state", root / "state.json", reference_root=root)
    create_directory(context, directory)
    publish_json(context, directory / "state-snapshot.json", state, kind="series_state")
    checks, prefixes = [], []
    def record(check_id, function, artifact=None):
        try:
            function()
            checks.append({"check_id": check_id, "status": "passed", "message": "Verified", "artifact": artifact, "json_pointer": None})
        except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
            checks.append({"check_id": check_id, "status": "failed", "message": str(exc) or type(exc).__name__, "artifact": artifact, "json_pointer": None})
    def plan_state():
        if state["series_id"] != plan["series_id"] or state["plan_sha256"] != file_ref(root / "plan.json", root)["sha256"]:
            raise DocumentError("Plan/state identity differs")
        if [item["job_id"] for item in state["jobs"]] != [item["job_id"] for item in plan["jobs"]]:
            raise DocumentError("Status omitted or reordered jobs")
        active = [attempt for item in state["jobs"] for attempt in item["attempts"] if attempt["execution_status"] in ("launching", "running")]
        if len(active) > 1:
            raise DocumentError("More than one active case")
        for relative, sha256 in plan["frozen_files"].items():
            resolve_ref(root, {"path": relative, "sha256": sha256})
        for job in state["jobs"]:
            for attempt in job["attempts"]:
                path = root / attempt["directory"] / "manifest.json"
                if path.exists() and load_document("manifest", path, reference_root=root)["project_binding"] != plan["project_binding"]:
                    raise DocumentError("Attempt manifest project binding differs from its immutable series plan")
    record("plan-state-and-frozen-inputs", plan_state)
    record("materialization", lambda: verify_materialization(root, load_document("materialization_receipt", resolve_ref(root, plan["materialization_receipt"]), reference_root=root)))
    jobs = {job["job_id"]: job for job in plan["jobs"]}
    for job_state in state["jobs"]:
        job = jobs.get(job_state["job_id"])
        if job is None:
            continue
        for attempt in job_state["attempts"]:
            check_id = job["job_id"] + "-" + attempt["attempt_id"]
            if attempt["result"] is None:
                try:
                    ref = capture_prefix(root, attempt, directory / "prefixes" / (check_id + ".json"), context=context)
                    if ref is not None:
                        prefixes.append(ref)
                    checks.append({"check_id": check_id, "status": "passed" if ref else "not_applicable", "message": "Verified committed prefix" if ref else "No confirmed cursor; progress remains unknown",
                                   "artifact": ref, "json_pointer": None})
                except (OSError, ValueError, RuntimeError) as exc:
                    checks.append({"check_id": check_id, "status": "failed", "message": str(exc), "artifact": None, "json_pointer": None})
                continue
            def verify_attempt(job=job, attempt=attempt):
                path = resolve_ref(root, attempt["result"])
                result = verify_result(path, root, {"run_id": attempt["run_id"], "attempt_id": attempt["attempt_id"], "problem_id": job["problem_id"], "configuration_id": job["configuration_id"], "project_binding": plan["project_binding"]})
                if result["execution_status"] != attempt["execution_status"]:
                    raise DocumentError("Controller status differs from immutable result")
                if result["execution_stage"] == "solver":
                    problem = load_document("problem", resolve_ref(root, job["problem"]), reference_root=root)
                    oracle = load_document("oracle", resolve_ref(root, job["oracle"]), reference_root=root)
                    manifest = load_document("manifest", path.parent / "manifest.json", reference_root=root)
                    history_ref = manifest["inputs"]["initial_answers"]
                    initial = read_json(resolve_ref(root, history_ref))["answers"] if history_ref else []
                    journal = result["journal"]
                    prefix = verify_prefix(resolve_ref(root, {"path": journal["path"], "sha256": journal["sha256"]}).read_bytes(),
                        journal["valid_prefix_bytes"], journal["valid_prefix_sha256"], journal["last_good_sequence"], initial_answers=len(initial))
                    answers = initial + [{**event["payload"]["query"], "answer": event["payload"]["answer"]} for event in prefix["events"] if event["event_type"] == "answer_received"]
                    quality = evaluate_quality(problem, oracle, result["solver_result"]["selected_candidate_id"] if result["solver_result"] else None, answers)
                    if quality != result["quality"]:
                        raise DocumentError("Stored quality differs from independent rational oracle")
                    if quality["audit_status"] == "failed":
                        raise DocumentError("; ".join(quality["findings"]))
            record(check_id, verify_attempt, attempt["result"])
    is_partial = any(item["status"] in ("pending", "launching", "running") for item in state["jobs"])
    status = "failed" if any(item["status"] == "failed" for item in checks) else "partial" if is_partial else "passed"
    source, _, _ = loaded_source()
    report = {"schema_version": 1, "audit_id": str(UUID(directory.name)), "series_id": plan["series_id"], "created_at_utc": utc_now(), "auditor": source,
        "plan": file_ref(root / "plan.json", root), "state": file_ref(directory / "state-snapshot.json", root), "prefix_snapshots": prefixes, "status": status, "checks": checks}
    publish_json(context, request.output_path, report, kind="audit")
    return AuditOutcome(Path(request.output_path), report, 1 if status == "failed" else 0)
