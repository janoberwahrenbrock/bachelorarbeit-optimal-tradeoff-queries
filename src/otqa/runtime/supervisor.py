"""One supervised CaseProcess path for standalone solves and series attempts."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

from .case import bootstrap_result, error_wire, timings
from .codec import DocumentError, digest, read_json, utc_now
from .documents import file_ref, load_answer_history, load_config_document, load_execution_profile, load_oracle, load_problem, materialize_inputs, verified_closure
from .processes import group_status, identity_status, process_identity, terminate_owned_group
from .profiles import THREAD_VARIABLES, production_resolver
from .schema import validate
from .source import loaded_source
from .storage import create_directory, publish_json
from .project import bound_directory
from .validation import journal_policy, verify_result


class RecoveryBlockedError(RuntimeError):
    """Existing process ownership or durable stage is uncertain; no solver starts."""


def _confirm_group_end(identity, child):
    """Bounded read retries; no unknown group is signaled or assumed absent."""
    state = group_status(identity, owned_child=child)
    for _ in range(100):
        if state == "dead":
            return
        # On macOS the exact Popen child may already have exited while its
        # forkserver/tracker is still leaving the group. That transient state
        # is unknown, so retry the observation without granting any new start.
        time.sleep(0.01)
        state = group_status(identity, owned_child=child)
    raise RecoveryBlockedError("Case ended but its complete process group is still live or unknown")


def _validate_answer_selection(request, problem):
    if request.answer_source not in ("interactive", "simulated", "replay"):
        raise DocumentError("Unknown answer source")
    if (request.oracle_path is not None) != (request.answer_source == "simulated"):
        raise DocumentError("Only simulated answers require an oracle")
    if (request.replay_path is not None) != (request.answer_source == "replay"):
        raise DocumentError("Only replay answers require an answer script")
    root = request.source_root
    if request.oracle_path:
        load_oracle(request.oracle_path, problem, reference_root=root)
    if request.replay_path:
        load_answer_history(request.replay_path, problem, reference_root=root)
    if getattr(request, 'continuation_path', None) is not None and request.initial_answers_path is not None:
        raise DocumentError('Continuation and initial answer history are mutually exclusive')
    if request.initial_answers_path:
        load_answer_history(request.initial_answers_path, problem, reference_root=root)


def prepare_standalone(request, *, resolver=production_resolver) -> dict:
    context = request.context
    source_root = Path(request.source_root).resolve(strict=True)
    output = Path(request.output_dir).absolute()
    context.binding(output)
    if output.exists():
        raise DocumentError("Attempt output already exists")
    problem = load_problem(request.problem_path, reference_root=source_root)
    config = load_config_document(request.config_path, reference_root=source_root)
    if config['schema_version'] != 2:
        raise DocumentError('Native execution requires an explicit version-two configuration; convert it first')
    _validate_answer_selection(request, problem)
    profile = load_execution_profile(request.execution_profile_path, reference_root=source_root)
    verified = resolver(source_root, profile, "standalone")
    entries = {"problem": ("problem", request.problem_path), "configuration": ("config", request.config_path), "execution_profile": ("execution_profile", request.execution_profile_path)}
    for key, path in (("oracle", request.oracle_path), ("initial_answers", request.initial_answers_path), ("replay_answers", request.replay_path)):
        if path is not None:
            entries[key] = ("oracle" if key == "oracle" else "answer_history", path)
    if getattr(request, 'continuation_path', None) is not None:
        from .continuation import import_continuation
        source_for_continuation, _, _ = loaded_source()
        import_continuation(request.continuation_path, reference_root=source_root, problem=problem,
            configuration=config, source=source_for_continuation, profile=profile)
        entries['continuation'] = ('continuation', request.continuation_path)
    verified_closure(source_root, entries)
    source, inventory, provenance = loaded_source()
    create_directory(context, output)
    receipt = materialize_inputs(source_root, entries, output, context=context)
    publish_json(context, output / "source" / "inventory.json", inventory, kind="source_inventory")
    publish_json(context, output / "source" / "build-provenance.json", provenance, kind="source_build_provenance")
    refs = receipt["entrypoints"]
    return {"project_root": str(context.project_root), "reference_root": str(output), "attempt_dir": str(output),
        "project_binding": context.binding(output),
        "run_id": str(uuid4()), "attempt_id": "attempt0001", "series_id": None, "job_id": None,
        "problem_id": problem["problem_id"], "configuration_id": config["configuration_id"], "source": source,
        "source_inventory": file_ref(output / "source" / "inventory.json", output), "run_purpose": verified.run_purpose,
        "materialization_receipt": file_ref(output / "materialization_receipt.json", output),
        "inputs": {key: refs.get(key) for key in ("problem", "configuration", "oracle", "initial_answers", "replay_answers", "continuation")},
        "execution_profile": refs["execution_profile"], "answer_source": request.answer_source,
        "case_timeout_seconds": config["execution"]["case_timeout_seconds"], "native_threads": config["execution"]["native_threads"]}


def run_problem(request):
    payload = prepare_standalone(request)
    return supervise_attempt(payload, context=request.context)


def supervise_attempt(payload: dict, *, context, on_phase=None):
    """Reserve -> register -> durable grant -> one release pulse -> verify end."""
    from otqa.application_types import RunOutcome
    attempt, root = Path(payload["attempt_dir"]), Path(payload["reference_root"])
    owner = uuid4().hex
    controller = process_identity(owner)
    nonce = uuid4().hex
    # Payload is immutable host-operation metadata, never a new solver config.
    publish_json(context, attempt / "case-request.json", payload)
    started = utc_now()
    controller_t0 = time.perf_counter()
    intent = {"schema_version": 1, "run_id": payload["run_id"], "attempt_id": payload["attempt_id"], "series_id": payload["series_id"], "job_id": payload["job_id"],
        "problem_id": payload["problem_id"], "configuration_id": payload["configuration_id"], "created_at_utc": started, "owner_token": owner,
        "nonce": nonce, "controller": controller, "materialization_receipt": payload["materialization_receipt"]}
    publish_json(context, attempt / "launch_intent.json", intent, kind="launch_intent")
    intent_ref = file_ref(attempt / "launch_intent.json", root)
    if on_phase:
        on_phase("launching", {"intent": intent_ref, "process": None})
    read_fd, write_fd = os.pipe()
    env = dict(os.environ)
    for variable in THREAD_VARIABLES:
        env[variable] = str(payload["native_threads"])
    # Neither arbitrary environment nor PYTHONPATH introduces a source adapter.
    env.pop("PYTHONPATH", None)
    child = identity = None
    log_stream = None
    release_sent = False
    interruption = None
    try:
        with bound_directory(context, attempt / "logs", create=True) as logs:
            log_fd = os.open("stderr.txt", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=logs)
            log_stream = os.fdopen(log_fd, "wb", buffering=0)
        child = subprocess.Popen([sys.executable, "-m", "otqa.runtime.case", "--request", str(attempt / "case-request.json"), "--release-fd", str(read_fd)],
            pass_fds=(read_fd,), start_new_session=True, env=env, cwd=str(context.project_root), stdin=None,
            stdout=log_stream, stderr=None if payload["answer_source"] == "interactive" else log_stream)
        os.close(read_fd)
        read_fd = None
        # Registration is written before the child can read the release pulse.
        while not (attempt / "child_registration.json").exists():
            if child.poll() is not None:
                break
            time.sleep(0.01)
        if (attempt / "child_registration.json").exists():
            registration = validate("child_registration", read_json(attempt / "child_registration.json"))
            identity = registration["process"]
            if registration["intent"] != intent_ref or registration["nonce"] != nonce or registration["run_id"] != payload["run_id"] or registration["attempt_id"] != payload["attempt_id"]:
                raise RecoveryBlockedError("Child registration is not bound to its reserved intent")
            if identity["pid"] != child.pid or identity["owner_token"] != owner or identity_status(identity, owned_child=child) != "alive" or group_status(identity, owned_child=child) != "alive":
                raise RecoveryBlockedError("Registered child identity/session is not demonstrably owned and live")
            registration_ref = file_ref(attempt / "child_registration.json", root)
            if on_phase:
                on_phase("registered", {"registration": registration_ref, "process": identity})
            grant = {"schema_version": 1, "run_id": payload["run_id"], "attempt_id": payload["attempt_id"], "created_at_utc": utc_now(),
                "intent": intent_ref, "registration": registration_ref, "nonce": nonce, "process": identity}
            publish_json(context, attempt / "start_grant.json", grant, kind="start_grant")
            if on_phase:
                on_phase("granted", {"grant": file_ref(attempt / "start_grant.json", root), "process": identity})
            released_at = time.perf_counter()
            os.write(write_fd, b"G")
            release_sent = True
            os.close(write_fd)
            write_fd = None
            if on_phase:
                on_phase("running", {"process": identity})
            accepted_terminal = False
            while child.poll() is None:
                if not accepted_terminal and (attempt / "result.json").exists():
                    verify_result(attempt / "result.json", root, payload)
                    accepted_terminal = True
                deadline = payload["case_timeout_seconds"]
                if not accepted_terminal and deadline is not None and time.perf_counter() - released_at > deadline:
                    interruption = {"reason": "timeout", "message": f"External case watchdog expired after {deadline} seconds"}
                    terminate_owned_group(identity, owned_child=child, force=True)
                    break
                time.sleep(0.025)
        # A child without registration sees EOF, and therefore cannot start.
        if write_fd is not None:
            os.close(write_fd)
            write_fd = None
        child.wait()
    except KeyboardInterrupt:
        interruption = {"reason": "user_cancel", "message": "User interrupted the supervisor"}
        if identity is not None and group_status(identity, owned_child=child) == "alive":
            terminate_owned_group(identity, owned_child=child, force=True)
        elif child is not None and child.poll() is None:
            # Before registration this exact Popen child has not been released.
            child.kill()
        if child is not None:
            child.wait()
    except BaseException as exc:
        if child is None:
            result = bootstrap_result(payload, started, None, error=error_wire(exc), finalized_by="controller")
            publish_json(context, attempt / "result.json", result, kind="result")
        else:
            if not release_sent and child.poll() is None:
                # Closing the private release writer is the pre-release EOF contract.
                if write_fd is not None:
                    os.close(write_fd)
                    write_fd = None
                child.wait()
            raise
    finally:
        for descriptor in (read_fd, write_fd):
            if descriptor is not None:
                os.close(descriptor)
        if log_stream is not None:
            os.fsync(log_stream.fileno())
            log_stream.close()

    if identity is not None:
        # Retrying a read is not a kill deadline or a successful cleanup claim.
        _confirm_group_end(identity, child)
    if not (attempt / "result.json").exists():
        if not release_sent:
            result = bootstrap_result(payload, started, None,
                interruption=interruption or {"reason": "controller_lost", "message": "Bootstrap child ended before release"}, finalized_by="controller")
            publish_json(context, attempt / "result.json", result, kind="result")
        else:
            finalize_ended_attempt(payload, context=context, interruption=interruption)
    result = verify_result(attempt / "result.json", root, payload)
    elapsed = time.perf_counter() - controller_t0
    if on_phase:
        on_phase("terminal", {"result": file_ref(attempt / "result.json", root), "document": result, "controller_elapsed_seconds": elapsed})
    code = 130 if result["execution_status"] == "interrupted" and result["interruption"]["reason"] == "user_cancel" else 1 if result["execution_status"] != "completed" else 0 if result["solver_result"]["solved"] else 3
    return RunOutcome(attempt / "result.json", result, code)



def finalize_ended_attempt(payload, *, context, interruption=None):
    """Conservative finalization after caller proved all owned processes ended."""
    attempt, root = Path(payload["attempt_dir"]), Path(payload["reference_root"])
    if not (attempt / "progress.json").exists():
        # A grant/manifest/readable run_started line does not prove cursor return.
        if (attempt / "events.jsonl").exists() and (attempt / "events.jsonl").stat().st_size:
            raise RecoveryBlockedError("Start bytes exist without a confirmed start cursor; stage remains uncertain")
        result = bootstrap_result(payload, utc_now(), None,
            interruption=interruption or {"reason": "controller_lost", "message": "Child ended before a solver start"}, finalized_by="controller")
        publish_json(context, attempt / "result.json", result, kind="result")
        return
    cursor = validate("progress", read_json(attempt / "progress.json"))
    from .journal import verify_cursor
    data = (attempt / "events.jsonl").read_bytes()
    manifest = validate("manifest", read_json(attempt / "manifest.json"))
    if manifest["project_binding"] != payload.get("project_binding", context.binding(root)):
        raise RecoveryBlockedError("Stored manifest project binding differs from this run")
    verified = verify_cursor(data, cursor, **journal_policy(manifest, root, attempt / "manifest.json"))
    if verified["query_counts"] != cursor["query_counts"] or cursor["run_id"] != payload["run_id"] or cursor["attempt_id"] != payload["attempt_id"]:
        raise RecoveryBlockedError("Stored cursor is not a valid binding for this run")
    result = {"schema_version": 2, "run_id": payload["run_id"], "attempt_id": payload["attempt_id"], "problem_id": payload["problem_id"], "configuration_id": payload["configuration_id"],
        "execution_status": "interrupted", "execution_stage": "solver", "finalized_by": "controller", "started_at_utc": verified["started_at_utc"], "finished_at_utc": utc_now(),
        "query_counts": cursor["query_counts"], "timings": timings(partial=cursor["partial_api_elapsed_seconds"]), "solver_result": None,
        "quality": {"status": "not_selected", "audit_status": "not_available", "true_winner_ids": [], "regret_fraction": None, "findings": []},
        "error": None, "interruption": interruption or {"reason": "controller_lost", "message": "Owned group ended without a terminal result"}, "telemetry_errors": [],
        "journal": {"path": (attempt / "events.jsonl").relative_to(root).as_posix(), "sha256": digest(data), "bytes": len(data), "valid_prefix_bytes": cursor["valid_prefix_bytes"],
            "valid_prefix_sha256": cursor["valid_prefix_sha256"], "last_good_sequence": cursor["last_good_sequence"], "trailing_partial_line": bool(data and not data.endswith(b"\n")),
            "uncommitted_suffix_bytes": len(data) - cursor["valid_prefix_bytes"]}, "numeric_hex": {}}
    publish_json(context, attempt / "result.json", result, kind="result")
