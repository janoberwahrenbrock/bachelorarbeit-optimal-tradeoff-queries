"""Frozen plans and a serial controller retaining every job and attempt."""
from __future__ import annotations

import fcntl
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from otqa.runtime.codec import DocumentError, digest, read_json, utc_now
from otqa.runtime.documents import file_ref, load_document, load_execution_profile, load_oracle, materialize_inputs, resolve_ref, verified_closure
from otqa.runtime.processes import group_status, process_identity
from otqa.runtime.ownership import verified_process_chain
from otqa.runtime.profiles import production_resolver
from otqa.runtime.project import bound_directory, verify_binding
from otqa.runtime.source import loaded_source, same_source
from otqa.runtime.storage import create_directory, publish_json
from otqa.runtime.schema import latest_version
from otqa.runtime.supervisor import RecoveryBlockedError, finalize_ended_attempt, supervise_attempt, verify_result
from otqa.runtime.validation import journal_policy

from .suite import ordered_jobs


def _scope():
    return "series_linux_recovery" if sys.platform.startswith("linux") else "standalone"


def plan_suite(request, *, resolver=production_resolver):
    from otqa.application_types import PlanOutcome
    context = request.context
    root = Path(request.source_root).resolve(strict=True)
    output = Path(request.output_dir).absolute()
    context.binding(output)
    if output.exists():
        raise DocumentError("Series output already exists")
    suite = load_document("suite", request.suite_path, reference_root=root)
    dataset = load_document("dataset", resolve_ref(root, suite["dataset"]), reference_root=root)
    # Check configuration identity and every selected case before reserving output.
    for ref in suite["configurations"]:
        document = load_document("config", resolve_ref(root, {key: ref[key] for key in ("path", "sha256")}), reference_root=root)
        if document["schema_version"] != latest_version("config"):
            raise DocumentError("New series require explicitly converted current configurations")
        if document["configuration_id"] != ref["configuration_id"]:
            raise DocumentError("Suite configuration ID differs from referenced document")
    for case in dataset["cases"]:
        problem = load_document("problem", resolve_ref(root, case["problem"]), reference_root=root)
        load_oracle(resolve_ref(root, case["oracle"]), problem, reference_root=root)
    ordered_jobs(suite, dataset, root)
    profile = load_execution_profile(request.execution_profile_path, reference_root=root)
    verified = resolver(root, profile, _scope())
    entries = {"suite": ("suite", request.suite_path), "execution_profile": ("execution_profile", request.execution_profile_path)}
    verified_closure(root, entries)
    source, inventory, provenance = loaded_source()
    create_directory(context, output)
    receipt = materialize_inputs(root, entries, output, context=context)
    publish_json(context, output / "source" / "inventory.json", inventory, kind="source_inventory")
    publish_json(context, output / "source" / "build-provenance.json", provenance, kind="source_build_provenance")
    suite_ref = receipt["entrypoints"]["suite"]
    native_suite = load_document("suite", resolve_ref(output, suite_ref), reference_root=output)
    native_dataset = load_document("dataset", resolve_ref(output, native_suite["dataset"]), reference_root=output)
    jobs = ordered_jobs(native_suite, native_dataset, output)
    frozen = {path.relative_to(output).as_posix(): digest(path.read_bytes()) for path in sorted(output.rglob("*")) if path.is_file()}
    series_id = str(uuid4())
    plan = {"schema_version": latest_version("series_plan"), "series_id": series_id, "suite_id": suite["suite_id"], "created_at_utc": utc_now(),
        "source": source, "project_binding": context.binding(output), "execution_profile": receipt["entrypoints"]["execution_profile"],
        "suite": suite_ref, "dataset": native_suite["dataset"], "frozen_files": frozen, "jobs": jobs,
        "run_purpose": verified.run_purpose, "materialization_receipt": file_ref(output / "materialization_receipt.json", output)}
    publish_json(context, output / "plan.json", plan, kind="series_plan")
    state = {"schema_version": latest_version("series_state"), "series_id": series_id, "plan_sha256": file_ref(output / "plan.json", output)["sha256"], "revision": 1,
        "updated_at_utc": utc_now(), "status": "planned", "controller": None, "active_job_id": None,
        "jobs": [{"job_id": job["job_id"], "status": "pending", "attempts": []} for job in jobs]}
    publish_json(context, output / "state.json", state, kind="series_state")
    return PlanOutcome(output, output / "plan.json", plan)


def load_series(series_dir, *, context, resolver=production_resolver):
    root = Path(series_dir).absolute()
    plan = load_document("series_plan", root / "plan.json", reference_root=root)
    verify_binding(context, root, plan["project_binding"])
    state = load_document("series_state", root / "state.json", reference_root=root)
    if state["series_id"] != plan["series_id"] or state["plan_sha256"] != file_ref(root / "plan.json", root)["sha256"]:
        raise DocumentError("Series state does not bind this immutable plan")
    if [job["job_id"] for job in state["jobs"]] != [job["job_id"] for job in plan["jobs"]]:
        raise DocumentError("Series state omitted, added or reordered planned jobs")
    _verify_manifest_bindings(root, plan, state)
    for relative, sha256 in plan["frozen_files"].items():
        resolve_ref(root, {"path": relative, "sha256": sha256})
    source, _, _ = loaded_source()
    if not same_source(plan["source"], source):
        raise DocumentError("Actual production source differs from the frozen series")
    profile = load_execution_profile(resolve_ref(root, plan["execution_profile"]), reference_root=root)
    verified = resolver(root, profile, _scope())
    if verified.run_purpose != plan["run_purpose"]:
        raise DocumentError("Production cannot run or resume a qualification plan")
    return root, plan, state


def _verify_manifest_bindings(root, plan, state):
    for job in state["jobs"]:
        for attempt in job["attempts"]:
            path = root / attempt["directory"] / "manifest.json"
            if path.exists():
                manifest = load_document("manifest", path, reference_root=root)
                if manifest["project_binding"] != plan["project_binding"]:
                    raise DocumentError("Attempt manifest project binding differs from its immutable series plan")


@contextmanager
def controller_lock(root, context):
    with bound_directory(context, root) as directory:
        descriptor = os.open("controller.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o644, dir_fd=directory)
        try:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RecoveryBlockedError("Another controller owns this series lock") from exc
            yield
        finally:
            os.close(descriptor)


def _save(context, root, state):
    state["revision"] += 1
    state["updated_at_utc"] = utc_now()
    publish_json(context, root / "state.json", state, kind="series_state", replace=True)


def _attempt_payload(root, plan, job, attempt, source):
    config = load_document("config", resolve_ref(root, job["configuration"]), reference_root=root)
    return {"project_root": str(root.parents[len(Path(plan["project_binding"]["relative_root"]).parts) - 1]),
        "project_binding": plan["project_binding"],
        "reference_root": str(root), "attempt_dir": str(root / attempt["directory"]), "run_id": attempt["run_id"], "attempt_id": attempt["attempt_id"],
        "series_id": plan["series_id"], "job_id": job["job_id"], "problem_id": job["problem_id"], "configuration_id": job["configuration_id"], "source": source,
        "source_inventory": file_ref(root / "source" / "inventory.json", root), "run_purpose": plan["run_purpose"], "materialization_receipt": plan["materialization_receipt"],
        "inputs": {"problem": job["problem"], "configuration": job["configuration"], "oracle": job["oracle"], "initial_answers": None, "replay_answers": None, "continuation": None},
        "execution_profile": plan["execution_profile"], "answer_source": "simulated", "case_timeout_seconds": config["execution"]["case_timeout_seconds"], "native_threads": config["execution"]["native_threads"]}


def run_suite(plan_path: Path, *, context):
    return _execute(Path(plan_path).parent, context=context, resume=False)


def resume_suite(series_dir: Path, *, context):
    return _execute(series_dir, context=context, resume=True)


def _recover(root, plan, state, context):
    source, _, _ = loaded_source()
    planned = {job["job_id"]: job for job in plan["jobs"]}
    for job_state in state["jobs"]:
        for attempt in job_state["attempts"]:
            job = planned[job_state["job_id"]]
            identities = {"run_id": attempt["run_id"], "attempt_id": attempt["attempt_id"],
                "series_id": plan["series_id"], "job_id": job["job_id"],
                "problem_id": job["problem_id"], "configuration_id": job["configuration_id"], "project_binding": plan["project_binding"]}
            if attempt["execution_status"] not in ("launching", "running"):
                if attempt["result"] is None:
                    raise RecoveryBlockedError("Terminal attempt lacks its immutable result")
                result = verify_result(resolve_ref(root, attempt["result"]), root, identities)
                if result["execution_status"] != attempt["execution_status"]:
                    raise RecoveryBlockedError("Terminal controller status differs from its immutable result")
                try:
                    identity, _, _ = verified_process_chain(root, root / attempt["directory"],
                        identities=identities, intent_ref=attempt["launch_intent"],
                        registration_ref=attempt["child_registration"], grant_ref=attempt["start_grant"],
                        recorded_process=attempt["process"])
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    raise RecoveryBlockedError("Unverified terminal process/launch chain") from exc
                if identity is not None and group_status(identity) != "dead":
                    raise RecoveryBlockedError("A terminal attempt still has a live or unknown group")
                if identity is None and result["execution_stage"] != "bootstrap":
                    raise RecoveryBlockedError("Solver attempt lacks an immutable process identity")
                continue
            directory = root / attempt["directory"]
            try:
                identity, registration, grant = verified_process_chain(root, directory,
                    identities=identities, intent_ref=attempt["launch_intent"],
                    registration_ref=attempt["child_registration"], grant_ref=attempt["start_grant"],
                    recorded_process=attempt["process"], running=attempt["execution_status"] == "running")
            except (OSError, ValueError, KeyError, TypeError) as exc:
                raise RecoveryBlockedError("Unverified prior process/launch chain; no second solver may start") from exc
            if identity is None:
                # No nonce-bearing registration means the spawn gap cannot be
                # inferred away merely because a file/process is absent now.
                raise RecoveryBlockedError("Unregistered spawn remains uncertain; no second solver may start")
            if group_status(identity) != "dead":
                raise RecoveryBlockedError("A prior solver group is alive or cannot be proven ended")
            attempt["process"] = identity
            attempt["child_registration"] = registration
            attempt["start_grant"] = grant
            payload = _attempt_payload(root, plan, planned[job_state["job_id"]], attempt, source)
            payload["project_root"] = str(context.project_root)
            if not (directory / "result.json").exists():
                finalize_ended_attempt(payload, context=context)
            result = verify_result(directory / "result.json", root, payload)
            attempt["execution_status"] = result["execution_status"]
            attempt["result"] = file_ref(directory / "result.json", root)
            job_state["status"] = result["execution_status"]
            _save(context, root, state)


def _execute(series_dir, *, context, resume, resolver=production_resolver):
    from otqa.application_types import SeriesOutcome
    root, plan, state = load_series(series_dir, context=context, resolver=resolver)
    with controller_lock(root, context):
        # Re-read after acquiring the exclusive controller lease.
        root, plan, state = load_series(root, context=context, resolver=resolver)
        if not resume and any(job["attempts"] for job in state["jobs"]):
            raise DocumentError("Series already started; use benchmark resume")
        if resume:
            _recover(root, plan, state, context)
        state["controller"] = process_identity(uuid4().hex)
        state["status"] = "running"
        _save(context, root, state)
        source, _, _ = loaded_source()
        try:
            for job, job_state in zip(plan["jobs"], state["jobs"]):
                if job_state["status"] in ("completed", "failed"):
                    continue
                # Every retry uses original fresh inputs and a distinct attempt.
                index = len(job_state["attempts"]) + 1
                attempt_id = f"attempt{index:04d}"
                relative = f"jobs/{job['job_id']}/attempts/{attempt_id}"
                directory = root / relative
                create_directory(context, directory)
                attempt = {"attempt_id": attempt_id, "run_id": str(uuid4()), "directory": relative, "execution_status": "launching",
                    "launch_intent": None, "child_registration": None, "start_grant": None, "process": None, "result": None, "controller_elapsed_seconds": None}
                # A launching attempt becomes visible only with its real durable
                # Intent FileRef, supplied by the shared supervisor callback.
                payload = _attempt_payload(root, plan, job, attempt, source)
                payload["project_root"] = str(context.project_root)
                def update(phase, info):
                    if phase == "launching":
                        attempt["launch_intent"] = info["intent"]
                        job_state["attempts"].append(attempt)
                        job_state["status"] = "launching"
                        state["active_job_id"] = job["job_id"]
                    elif phase == "registered":
                        attempt["child_registration"] = info["registration"]
                        attempt["process"] = info["process"]
                    elif phase == "granted":
                        attempt["start_grant"] = info["grant"]
                    elif phase == "running":
                        attempt["execution_status"] = job_state["status"] = "running"
                    elif phase == "terminal":
                        attempt["result"] = info["result"]
                        attempt["execution_status"] = job_state["status"] = info["document"]["execution_status"]
                        attempt["controller_elapsed_seconds"] = info["controller_elapsed_seconds"]
                        state["active_job_id"] = None
                    _save(context, root, state)
                outcome = supervise_attempt(payload, context=context, on_phase=update)
                if outcome.exit_code == 130:
                    state["status"] = "interrupted"
                    state["controller"] = None
                    _save(context, root, state)
                    return SeriesOutcome(root, state, 130)
            failures = any(job["status"] in ("failed", "interrupted") for job in state["jobs"])
            state["status"] = "completed_with_failures" if failures else "completed"
            state["controller"], state["active_job_id"] = None, None
            _save(context, root, state)
            if failures:
                code = 1
            else:
                results = [read_json(resolve_ref(root, job["attempts"][-1]["result"])) for job in state["jobs"]]
                code = 3 if any(not result["solver_result"]["solved"] for result in results) else 0
            return SeriesOutcome(root, state, code)
        except BaseException:
            state["status"] = "interrupted"
            # Preserve active job and original attempt state; no synthetic failure.
            state["controller"] = None
            _save(context, root, state)
            raise


def inspect_series(series_dir, *, context, _allow_qualification=False):
    from otqa.application_types import SeriesStatus
    # Status is a reader. A qualification series is readable without granting it
    # production execution, so no admission resolver is invoked here.
    root = Path(series_dir).absolute()
    plan = load_document("series_plan", root / "plan.json", reference_root=root)
    verify_binding(context, root, plan["project_binding"])
    if plan["run_purpose"] != "production" and not _allow_qualification:
        raise DocumentError("Public series commands accept production plans only")
    state = load_document("series_state", root / "state.json", reference_root=root)
    if state["plan_sha256"] != file_ref(root / "plan.json", root)["sha256"] or state["series_id"] != plan["series_id"]:
        raise DocumentError("State/plan binding differs")
    _verify_manifest_bindings(root, plan, state)
    processes, warnings = [], []
    for job in state["jobs"]:
        for attempt in job["attempts"]:
            if attempt["execution_status"] not in ("launching", "running"):
                continue
            identity = attempt["process"]
            registration = root / attempt["directory"] / "child_registration.json"
            if identity is None and registration.exists():
                identity = load_document("child_registration", registration, reference_root=root)["process"]
            status = "unknown" if identity is None else group_status(identity)
            progress = None
            progress_path = root / attempt["directory"] / "progress.json"
            if progress_path.exists():
                from otqa.runtime.journal import verify_cursor
                cursor = load_document("progress", progress_path, reference_root=root)
                manifest = load_document("manifest", progress_path.parent / "manifest.json", reference_root=root)
                data = (progress_path.parent / "events.jsonl").read_bytes()
                verified = verify_cursor(data, cursor, **journal_policy(manifest, root, progress_path.parent / "manifest.json"))
                if verified["query_counts"] != cursor["query_counts"] or cursor["run_id"] != attempt["run_id"] or cursor["process"] != manifest["process"]:
                    raise DocumentError("Live status cursor binding differs")
                progress = cursor
            processes.append({"job_id": job["job_id"], "attempt_id": attempt["attempt_id"], "identity": identity, "group_status": status, "progress": progress})
            if status == "unknown":
                warnings.append(f"Process ownership is unknown for {job['job_id']}/{attempt['attempt_id']}")
    return SeriesStatus(root, plan, state, tuple(processes), tuple(warnings))
