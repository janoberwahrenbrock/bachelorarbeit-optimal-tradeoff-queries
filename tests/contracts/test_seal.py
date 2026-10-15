"""Native archive controls use only independently constructed synthetic files."""
import copy
import fcntl
import hashlib
import json
import os
import shutil
from uuid import uuid4

import pytest

from otqa.analysis import seal
from otqa.runtime.codec import DocumentError, decode, encode
from otqa.runtime.project import load_project_context
from otqa.runtime.schema import definitions


@pytest.fixture
def terminal_series(tmp_path, monkeypatch):
    project_id, series_id, run_id = str(uuid4()), str(uuid4()), str(uuid4())
    (tmp_path / "otqa-project.json").write_bytes(encode({"schema_version": 1, "project_kind": "otqa_project", "project_id": project_id}))
    context = load_project_context(tmp_path)
    root = tmp_path / "runs" / "original"
    root.mkdir(parents=True)
    (root / "controller.lock").touch()
    (root / "payload").mkdir()
    (root / "payload" / "raw.bin").write_bytes(b"\x00native\xff\r\n")
    (root / "payload" / "provenance.json").write_bytes(b'{ "unchanged": -0.0 }\n')
    def ref(p):
        return {"path": p, "sha256": hashlib.sha256((root / p).read_bytes()).hexdigest()}
    dummy = {"path": "payload/raw.bin", "sha256": ref("payload/raw.bin")["sha256"]}
    plan = {"schema_version": 1, "series_id": series_id, "suite_id": "suite", "created_at_utc": "2026-01-01T00:00:00Z",
        "source": {"inventory_format": "otqa-source-v1", "version": "0.1.0", "git_commit": None, "dirty": False, "source_sha256": "a" * 64},
        "project_binding": context.binding(root), "execution_profile": dummy, "suite": dummy, "dataset": dummy,
        "frozen_files": {"payload/raw.bin": dummy["sha256"]}, "run_purpose": "production", "materialization_receipt": dummy,
        "jobs": [{"job_id": "job", "case_id": "case", "problem_id": "problem", "configuration_id": "config", "repetition_index": 0,
                  "problem": dummy, "oracle": dummy, "configuration": dummy}]}
    (root / "plan.json").write_bytes(encode(plan))
    identity = {"pid": 987654321, "hostname": "synthetic", "identity_method": "owned_child", "boot_id": None,
                "start_ticks": None, "pgid": 987654321, "sid": 987654321, "owner_token": "test"}
    intent = {"schema_version": 1, "run_id": run_id, "attempt_id": "attempt", "series_id": series_id, "job_id": "job",
              "problem_id": "problem", "configuration_id": "config", "created_at_utc": "2026-01-01T00:00:00Z",
              "owner_token": "test", "nonce": "nonce", "controller": identity, "materialization_receipt": dummy}
    (root / "launch_intent.json").write_bytes(encode(intent))
    registration = {"schema_version": 1, "run_id": run_id, "attempt_id": "attempt", "created_at_utc": "2026-01-01T00:00:00Z",
                    "intent": ref("launch_intent.json"), "nonce": "nonce", "process": identity}
    (root / "child_registration.json").write_bytes(encode(registration))
    result = {"schema_version": 1, "run_id": run_id, "attempt_id": "attempt",
        "problem_id": "problem", "configuration_id": "config", "execution_status": "failed", "execution_stage": "bootstrap",
        "finalized_by": "controller", "started_at_utc": "2026-01-01T00:00:00Z", "finished_at_utc": "2026-01-01T00:00:01Z",
        "query_counts": {"initial_answers": 0, "dispatched_new": 0, "answered_new": 0, "answered_total": 0},
        "timings": {k: None for k in definitions()[0]["Timings"]["properties"] if k not in ("scope_version", "complete_api_measurement")},
        "solver_result": None, "quality": {"status": "not_selected", "audit_status": "not_available", "true_winner_ids": [], "regret_fraction": None, "findings": []},
        "error": {"code": "worker_failure", "type": "SyntheticError", "message": "constructed terminal failure", "traceback": None, "stage": "worker", "context": {}},
        "interruption": None, "telemetry_errors": [], "journal": None, "numeric_hex": {}}
    result["timings"].update(scope_version=1, complete_api_measurement=False)
    (root / "result.json").write_bytes(encode(result))
    attempt = {"attempt_id": "attempt", "run_id": run_id, "directory": ".", "execution_status": "failed", "launch_intent": ref("launch_intent.json"),
               "child_registration": ref("child_registration.json"), "start_grant": None, "process": identity, "result": ref("result.json"), "controller_elapsed_seconds": None}
    state = {"schema_version": 1, "series_id": series_id, "plan_sha256": ref("plan.json")["sha256"], "revision": 1,
             "updated_at_utc": "2026-01-01T00:00:01Z", "status": "completed_with_failures", "controller": None, "active_job_id": None,
             "jobs": [{"job_id": "job", "status": "failed", "attempts": [attempt]}]}
    (root / "state.json").write_bytes(encode(state))
    monkeypatch.setattr(seal, "group_status", lambda identity: "dead")
    return context, root, state


def destination(context):
    return context.project_root / "runs" / "archive" / "archive_inventory.json"


def test_portable_seal_copies_each_file_once_and_keeps_original_bindings(terminal_series, tmp_path):
    context, root, _ = terminal_series
    original = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    output = root / "seals" / str(uuid4()) / "archive_inventory.json"
    ref = seal.seal_inventory(context, root, output)
    inventory = seal.verify_seal(output.parent)
    assert ref == {"path": "archive_inventory.json", "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
    files = inventory["files"]
    assert [x["path"] for x in files] == sorted(original)
    assert inventory["inventory_sha256"] == hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert all((output.parent / path).read_bytes() == data for path, data in original.items())
    assert decode((output.parent / "plan.json").read_bytes())["project_binding"] == context.binding(root)
    moved = tmp_path / "portable-copy"
    shutil.copytree(output.parent, moved)
    assert seal.verify_seal(moved) == inventory


@pytest.mark.parametrize("change", ["changed", "missing", "extra", "extra_directory", "symlink", "inventory_symlink"])
def test_verify_rejects_payload_corruption_and_uninventoried_paths(terminal_series, tmp_path, change):
    context, root, _ = terminal_series
    output = destination(context)
    seal.seal_series(context, root, output)
    payload = output.parent / "payload/raw.bin"
    if change == "changed":
        payload.write_bytes(b"changed")
    elif change == "missing":
        payload.unlink()
    elif change == "extra":
        (output.parent / "extra").touch()
    elif change == "extra_directory":
        (output.parent / "empty-extra").mkdir()
    elif change == "symlink":
        payload.unlink()
        payload.symlink_to(root / "payload/raw.bin")
    else:
        original = tmp_path / "inventory-copy"
        output.rename(original)
        output.symlink_to(original)
    with pytest.raises((DocumentError, OSError)):
        seal.verify_seal(output.parent)


@pytest.mark.parametrize("change", ["digest", "duplicate", "reorder", "self", "bytes"])
def test_verify_checks_canonical_sorted_complete_inventory(terminal_series, change):
    context, root, _ = terminal_series
    output = destination(context)
    seal.seal_inventory(context, root, output)
    doc = decode(output.read_bytes())
    if change == "digest":
        doc["inventory_sha256"] = "0" * 64
    elif change == "duplicate":
        doc["files"].append(copy.deepcopy(doc["files"][0]))
    elif change == "reorder":
        doc["files"].reverse()
    elif change == "self":
        doc["files"].append({"path": "archive_inventory.json", "bytes": 0, "sha256": "0" * 64})
        doc["files"].sort(key=lambda x: x["path"])
    else:
        doc["files"][0]["bytes"] += 1
    if change != "digest":
        doc["inventory_sha256"] = hashlib.sha256(json.dumps(doc["files"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output.write_bytes(encode(doc))
    with pytest.raises(DocumentError):
        seal.verify_seal(output.parent)


@pytest.mark.parametrize("status", ["alive", "unknown", None])
def test_live_or_unproven_groups_block_before_output_creation(terminal_series, monkeypatch, status):
    context, root, state = terminal_series
    if status is None:
        state["jobs"][0]["attempts"][0]["process"] = None
        state["jobs"][0]["attempts"][0]["child_registration"] = None
        (root / "child_registration.json").unlink()
        (root / "state.json").write_bytes(encode(state))
    else:
        monkeypatch.setattr(seal, "group_status", lambda identity: status)
    with pytest.raises(DocumentError, match="group"):
        seal.seal_inventory(context, root, destination(context))
    assert not destination(context).parent.exists()


@pytest.mark.parametrize("change", ["running", "pending", "missing_result", "controller", "active_job", "plan_binding"])
def test_nonterminal_and_mismatched_metadata_block_sealing(terminal_series, monkeypatch, change):
    context, root, state = terminal_series
    if change == "running":
        state["status"] = "running"
    elif change == "pending":
        state["jobs"][0]["status"] = "pending"
    elif change == "missing_result":
        state["jobs"][0]["attempts"][0]["result"] = None
    elif change == "controller":
        state["controller"] = state["jobs"][0]["attempts"][0]["process"]
        monkeypatch.setattr(seal, "identity_status", lambda identity: "unknown")
    elif change == "active_job":
        state["active_job_id"] = "job"
    else:
        state["plan_sha256"] = "0" * 64
    (root / "state.json").write_bytes(encode(state))
    with pytest.raises(DocumentError):
        seal.seal_inventory(context, root, destination(context))


def test_controller_lock_prevents_seal_during_owned_operation(terminal_series):
    context, root, _ = terminal_series
    fd = os.open(root / "controller.lock", os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(DocumentError, match="owns"):
            seal.seal_inventory(context, root, destination(context))
    finally:
        os.close(fd)


def test_output_conflicts_source_symlinks_and_project_escape_are_rejected(terminal_series, tmp_path):
    context, root, _ = terminal_series
    with pytest.raises(DocumentError):
        seal.seal_inventory(context, root, tmp_path / "outside/archive_inventory.json")
    with pytest.raises(DocumentError):
        seal.seal_inventory(context, root, root / "archive_inventory.json")
    (root / "alias").symlink_to(root / "payload/raw.bin")
    with pytest.raises(DocumentError):
        seal.seal_inventory(context, root, destination(context))
    (root / "alias").unlink()
    seal.seal_inventory(context, root, destination(context))
    original = destination(context).read_bytes()
    with pytest.raises(DocumentError):
        seal.seal_inventory(context, root, destination(context))
    assert destination(context).read_bytes() == original


def test_failed_copy_and_changed_source_leave_no_commit_marker(terminal_series, monkeypatch):
    context, root, _ = terminal_series
    original = seal._copy
    def change_after_copy(source, target, relative, stamp):
        value = original(source, target, relative, stamp)
        if relative == "controller.lock":
            (root / "payload/raw.bin").write_bytes(b"mutated during copy")
        return value
    monkeypatch.setattr(seal, "_copy", change_after_copy)
    with pytest.raises(DocumentError, match="changed"):
        seal.seal_inventory(context, root, destination(context))
    assert not destination(context).exists()
    with pytest.raises(OSError):
        seal.verify_seal(destination(context).parent)


def test_inventory_write_is_last_required_commit_barrier(terminal_series, monkeypatch):
    context, root, _ = terminal_series
    def fail_commit(directory, document):
        assert all((destination(context).parent / entry["path"]).is_file() for entry in document["files"])
        raise OSError("injected inventory barrier failure")
    monkeypatch.setattr(seal, "_commit", fail_commit)
    with pytest.raises(OSError):
        seal.seal_inventory(context, root, destination(context))
    assert not destination(context).exists()


def test_swapped_output_parent_cannot_redirect_copies_or_commit(terminal_series, monkeypatch, tmp_path):
    context, root, _ = terminal_series
    original = seal._copy
    target_parent = destination(context).parent
    outside = tmp_path / "untrusted"
    outside.mkdir()
    moved = context.project_root / "runs" / "bound-original"
    changed = False
    def swap(source, target, relative, stamp):
        nonlocal changed
        if not changed:
            target_parent.rename(moved)
            target_parent.symlink_to(outside, target_is_directory=True)
            changed = True
        return original(source, target, relative, stamp)
    monkeypatch.setattr(seal, "_copy", swap)
    with pytest.raises(DocumentError):
        seal.seal_inventory(context, root, destination(context))
    assert list(outside.iterdir()) == []
    assert not (moved / "archive_inventory.json").exists()


def test_mutable_dead_pid_cannot_replace_the_registered_process(terminal_series, monkeypatch):
    context, root, state = terminal_series
    state["jobs"][0]["attempts"][0]["process"] = {**state["jobs"][0]["attempts"][0]["process"], "pid": 987654320, "pgid": 987654320, "sid": 987654320}
    (root / "state.json").write_bytes(encode(state))
    checked = []
    monkeypatch.setattr(seal, "group_status", lambda process: checked.append(process) or "dead")
    with pytest.raises(DocumentError, match="immutable registration"):
        seal.seal_inventory(context, root, destination(context))
    assert checked == []


def test_inventory_fsync_failure_removes_the_commit_marker(terminal_series, monkeypatch):
    context, root, _ = terminal_series
    original_commit, real_sync = seal._commit, seal.os.fsync
    def fail_after_inventory_link(directory, document):
        def fail_sync(descriptor):
            if descriptor == directory:
                raise OSError("inventory directory barrier failed")
            return real_sync(descriptor)
        with monkeypatch.context() as local:
            local.setattr(seal.os, "fsync", fail_sync)
            original_commit(directory, document)
    monkeypatch.setattr(seal, "_commit", fail_after_inventory_link)
    with pytest.raises(OSError, match="barrier"):
        seal.seal_inventory(context, root, destination(context))
    assert not destination(context).exists()


def test_short_payload_write_is_completed_before_inventory_publication(terminal_series, monkeypatch):
    context, root, _ = terminal_series
    write = seal.os.write
    monkeypatch.setattr(seal.os, "write", lambda descriptor, data: write(descriptor, data[:3]))
    output = destination(context)
    seal.seal_inventory(context, root, output)
    assert seal.verify_seal(output.parent)["files"]


def test_external_inventory_reference_detects_a_coherently_replaced_bundle(terminal_series):
    context, root, _ = terminal_series
    output = destination(context)
    reference = seal.seal_inventory(context, root, output)
    assert seal.verify_seal(output.parent, inventory_ref=reference)
    payload = output.parent / "payload/raw.bin"
    payload.write_bytes(b"coherently replaced payload")
    inventory = decode(output.read_bytes())
    entry = next(x for x in inventory["files"] if x["path"] == "payload/raw.bin")
    entry.update(bytes=payload.stat().st_size, sha256=hashlib.sha256(payload.read_bytes()).hexdigest())
    inventory["inventory_sha256"] = hashlib.sha256(json.dumps(inventory["files"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    output.write_bytes(encode(inventory))
    assert seal.verify_seal(output.parent)
    with pytest.raises(DocumentError, match="external FileRef"):
        seal.verify_seal(output.parent, inventory_ref=reference)


def test_subsequent_seals_are_independent_without_recursive_archive_copies(terminal_series):
    context, root, _ = terminal_series
    first = root / "seals" / str(uuid4()) / "archive_inventory.json"
    second = root / "seals" / str(uuid4()) / "archive_inventory.json"
    seal.seal_inventory(context, root, first)
    seal.seal_inventory(context, root, second)
    left, right = seal.verify_seal(first.parent), seal.verify_seal(second.parent)
    assert left["files"] == right["files"]
    assert not any(entry["path"].startswith("seals/") for entry in right["files"])
    with pytest.raises(DocumentError, match="reserved seals/"):
        seal.seal_inventory(context, root, root / "reports/another/archive_inventory.json")


def test_declared_native_references_cannot_point_into_excluded_archives(terminal_series):
    context, root, _ = terminal_series
    native = {"schema_version": 1, "profile_id": "profile", "platform_family": "macos", "python_version": "3.13.4",
              "packages": {}, "backend_capabilities": {}, "environment_lock": {"path": "seals/previous/environment.txt", "sha256": "0" * 64},
              "certification": {"status": "illustrative_only", "evidence": None}}
    (root / "profile.json").write_bytes(encode(native))
    with pytest.raises(DocumentError, match="excluded seals/"):
        seal.seal_inventory(context, root, destination(context))
    native["environment_lock"]["path"] = "payload/raw.bin"
    # Free metadata is not an implicit FileRef position.
    native["backend_capabilities"] = {"metadata": {"path": "seals/inert", "sha256": "0" * 64}}
    (root / "profile.json").write_bytes(encode(native))
    seal.seal_inventory(context, root, destination(context))


def test_fifo_replacement_is_opened_nonblocking_and_rejected_by_fstat(terminal_series, monkeypatch):
    context, root, _ = terminal_series
    original_open = seal.os.open
    replaced = False
    def replace_with_fifo(path, flags, *args, **kwargs):
        nonlocal replaced
        if path == "raw.bin" and not replaced:
            replaced = True
            (root / "payload/raw.bin").unlink()
            os.mkfifo(root / "payload/raw.bin")
            assert flags & os.O_NONBLOCK
        return original_open(path, flags, *args, **kwargs)
    monkeypatch.setattr(seal.os, "supports_dir_fd", seal.os.supports_dir_fd | {replace_with_fifo})
    monkeypatch.setattr(seal.os, "open", replace_with_fifo)
    with pytest.raises(DocumentError, match="not a regular file"):
        seal.seal_inventory(context, root, destination(context))
    assert replaced


def solver_failure_fixture(root, state):
    """Construct a valid failed solver journal; no solver or native LP is run."""
    from otqa.numerics.profile import resolved_cache_policy, resolved_numerical_profile
    from otqa.runtime.codec import mathematical_hex
    def ref(name):
        return {"path": name, "sha256": hashlib.sha256((root / name).read_bytes()).hexdigest()}
    def write(name, document):
        (root / name).write_bytes(encode(document))
    plan = decode((root / "plan.json").read_bytes())
    attempt = state["jobs"][0]["attempts"][0]
    identity = attempt["process"]
    grant = {"schema_version": 1, "run_id": attempt["run_id"], "attempt_id": "attempt", "created_at_utc": "2026-01-01T00:00:00Z",
             "intent": ref("launch_intent.json"), "registration": ref("child_registration.json"), "nonce": "nonce", "process": identity}
    write("start_grant.json", grant)
    attempt["start_grant"] = ref("start_grant.json")
    policy = {"query_strategy": "fixed", "depth": 1, "higher_depth_query_source": "both", "grid_size": 5,
              "planning_evaluation": "candidate_count", "stopping": {"rule": "single_candidate"}}
    config = {"schema_version": 1, "configuration_id": "config", "algorithm": policy, "budget": {"max_queries": None},
              "execution": {"workers": 1, "start_method": "forkserver", "native_threads": 1, "case_timeout_seconds": None, "cache_policy_id": "bounded_v1"},
              "recording": {"durability": "per_answer", "trace_level": "standard", "profile": False, "telemetry_failure_policy": "continue"}}
    write("config.json", config)
    write("problem.json", {"schema_version": 1, "problem_id": "problem", "alternative_ids": ["a", "b"], "objective_ids": ["g0", "g1"], "alternatives": [[1.0, 0.0], [0.0, 1.0]]})
    dummy = ref("payload/raw.bin")
    manifest = {"schema_version": 1, "run_id": attempt["run_id"], "attempt_id": "attempt", "series_id": plan["series_id"], "job_id": "job", "problem_id": "problem", "configuration_id": "config",
                "execution_kind": "fresh", "answer_source": "simulated", "created_at_utc": "2026-01-01T00:00:00Z", "source": plan["source"], "source_inventory": dummy,
                "project_binding": plan["project_binding"], "run_purpose": "production", "materialization_receipt": dummy, "launch_intent": attempt["launch_intent"],
                "inputs": {"problem": ref("problem.json"), "configuration": ref("config.json"), "oracle": None, "initial_answers": None, "replay_answers": None},
                "mathematical_input_sha256": "0" * 64, "effective_algorithm": policy, "effective_budget": config["budget"], "effective_execution": config["execution"], "effective_recording": config["recording"],
                "execution_profile": dummy, "numerical_profile": resolved_numerical_profile(), "resolved_cache_policy": resolved_cache_policy(),
                "environment": {"hostname": "synthetic", "platform_family": "macos", "platform": "synthetic", "python": "3.13.4", "packages": {}, "cpu_model": None, "physical_cores": None, "logical_cpus": None, "native_thread_environment": {}, "backend_capabilities": {}}, "process": identity}
    write("manifest.json", manifest)
    result = decode((root / "result.json").read_bytes())
    payloads = [("run_started", {"manifest_sha256": ref("manifest.json")["sha256"]}), ("run_failed", {"error": result["error"], "query_counts": result["query_counts"]})]
    events = [{"schema_version": 1, "run_id": attempt["run_id"], "attempt_id": "attempt", "sequence": index,
               "occurred_at_utc": "2026-01-01T00:00:00Z", "monotonic_ns": index, "event_type": kind, "query_id": None,
               "payload": payload, "numeric_hex": mathematical_hex(payload, "/payload")} for index, (kind, payload) in enumerate(payloads, 1)]
    raw = b"".join(encode(event) for event in events)
    (root / "events.jsonl").write_bytes(raw)
    result["execution_stage"] = "solver"
    result["journal"] = {**ref("events.jsonl"), "bytes": len(raw), "valid_prefix_bytes": len(raw), "valid_prefix_sha256": hashlib.sha256(raw).hexdigest(), "last_good_sequence": 2, "trailing_partial_line": False, "uncommitted_suffix_bytes": 0}
    write("result.json", result)
    attempt["result"] = ref("result.json")
    write("state.json", state)


@pytest.mark.parametrize("corruption", [None, "journal", "problem", "config"])
def test_sealing_verifies_result_journal_manifest_and_input_hashes(terminal_series, corruption):
    context, root, state = terminal_series
    solver_failure_fixture(root, state)
    if corruption is None:
        seal.seal_inventory(context, root, destination(context))
        assert seal.verify_seal(destination(context).parent)
        return
    if corruption == "journal":
        with (root / "events.jsonl").open("ab") as stream:
            stream.write(b"corrupt later bytes\n")
    else:
        target = root / (corruption + ".json")
        data = decode(target.read_bytes())
        if corruption == "problem":
            data["alternatives"][0][0] = 0.5
        else:
            data["budget"]["max_queries"] = 3
        target.write_bytes(encode(data))
    with pytest.raises(DocumentError, match="hash differs"):
        seal.seal_inventory(context, root, destination(context))
    assert not destination(context).parent.exists()
