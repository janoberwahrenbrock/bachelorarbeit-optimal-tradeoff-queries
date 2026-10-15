import copy
import json
from uuid import uuid4

import pytest

from otqa.runtime.codec import DocumentError, digest, encode, utc_now
from otqa.runtime.ownership import verified_process_chain


def controls(tmp_path):
    root = tmp_path / "series"
    directory = root / "jobs" / "native-case" / "attempts" / "attempt0001"
    directory.mkdir(parents=True)
    ids = {"run_id": str(uuid4()), "attempt_id": "attempt0001", "series_id": str(uuid4()),
        "job_id": "native-case", "problem_id": "analytical", "configuration_id": "fixed2"}
    owner = uuid4().hex
    process = {"pid": 531, "hostname": "synthetic-chain-control", "identity_method": "owned_child",
        "boot_id": None, "start_ticks": None, "pgid": 531, "sid": 531, "owner_token": owner}
    intent = {"schema_version": 1, **ids, "created_at_utc": utc_now(), "owner_token": owner,
        "nonce": uuid4().hex, "controller": {**process, "pid": 211, "pgid": 211, "sid": 211},
        "materialization_receipt": {"path": "materialization_receipt.json", "sha256": "0" * 64}}
    def write(name, document):
        data = encode(document)
        (directory / name).write_bytes(data)
        return {"path": (directory / name).relative_to(root).as_posix(), "sha256": digest(data)}
    intent_ref = write("launch_intent.json", intent)
    registration = {"schema_version": 1, "run_id": ids["run_id"], "attempt_id": ids["attempt_id"],
        "created_at_utc": utc_now(), "intent": intent_ref, "nonce": intent["nonce"], "process": process}
    registration_ref = write("child_registration.json", registration)
    grant = {"schema_version": 1, "run_id": ids["run_id"], "attempt_id": ids["attempt_id"],
        "created_at_utc": utc_now(), "intent": intent_ref, "registration": registration_ref,
        "nonce": intent["nonce"], "process": process}
    grant_ref = write("start_grant.json", grant)
    values = {"identities": ids, "intent_ref": intent_ref, "registration_ref": registration_ref,
        "grant_ref": grant_ref, "recorded_process": process, "running": True}
    return root, directory, values, write


def test_complete_chain_binds_status_to_immutable_registration(tmp_path):
    root, directory, values, _ = controls(tmp_path)
    identity, registration, grant = verified_process_chain(root, directory, **values)
    assert identity == values["recorded_process"]
    assert registration == values["registration_ref"] and grant == values["grant_ref"]


def test_crash_after_publication_before_status_binding_discovers_verified_refs(tmp_path):
    root, directory, values, _ = controls(tmp_path)
    expected = values["recorded_process"]
    values.update(recorded_process=None, registration_ref=None, grant_ref=None, running=False)
    assert verified_process_chain(root, directory, **values)[0] == expected


@pytest.mark.parametrize("field", ["pid", "pgid", "sid", "owner_token", "start_ticks", "hostname"])
def test_mutable_status_cannot_substitute_another_dead_group(tmp_path, field):
    root, directory, values, _ = controls(tmp_path)
    values["recorded_process"] = copy.deepcopy(values["recorded_process"])
    values["recorded_process"][field] = "other" if field in ("owner_token", "hostname") else 999
    with pytest.raises(DocumentError):
        verified_process_chain(root, directory, **values)


@pytest.mark.parametrize("artifact,field", [
    ("launch_intent.json", "run_id"), ("launch_intent.json", "job_id"),
    ("child_registration.json", "run_id"), ("child_registration.json", "attempt_id"),
    ("child_registration.json", "nonce"), ("start_grant.json", "run_id"), ("start_grant.json", "nonce"),
])
def test_discovered_control_records_must_bind_ids_and_nonce(tmp_path, artifact, field):
    root, directory, values, write = controls(tmp_path)
    document = json.loads((directory / artifact).read_bytes())
    document[field] = str(uuid4()) if field == "run_id" else "other"
    replacement = write(artifact, document)
    values.update(registration_ref=None, grant_ref=None, running=False)
    if artifact == "launch_intent.json":
        values["intent_ref"] = replacement
    with pytest.raises(DocumentError):
        verified_process_chain(root, directory, **values)


def test_running_state_cannot_exist_without_a_grant(tmp_path):
    root, directory, values, _ = controls(tmp_path)
    (directory / "start_grant.json").unlink()
    values["grant_ref"] = None
    with pytest.raises(DocumentError, match="grant"):
        verified_process_chain(root, directory, **values)


def test_unregistered_reservation_preserves_unknown_spawn_state(tmp_path):
    root, directory, values, _ = controls(tmp_path)
    (directory / "child_registration.json").unlink()
    (directory / "start_grant.json").unlink()
    values.update(registration_ref=None, grant_ref=None, recorded_process=None, running=False)
    assert verified_process_chain(root, directory, **values) == (None, None, None)


def test_recovery_reader_rejects_symlink_artifact(tmp_path):
    root, directory, values, _ = controls(tmp_path)
    target = directory / "child_registration.json"
    actual = tmp_path / "registration-copy.json"
    target.rename(actual)
    target.symlink_to(actual)
    with pytest.raises(OSError):
        verified_process_chain(root, directory, **values)


def controller_fixture(tmp_path, monkeypatch, *, terminal=False):
    from otqa.experiments import controller
    root, directory, values, write = controls(tmp_path)
    ids = values["identities"]
    result_ref = write("result.json", {"test_fixture": "result reader is separately verified"}) if terminal else None
    attempt = {"run_id": ids["run_id"], "attempt_id": ids["attempt_id"],
        "directory": directory.relative_to(root).as_posix(), "execution_status": "completed" if terminal else "running",
        "launch_intent": values["intent_ref"], "child_registration": values["registration_ref"],
        "start_grant": values["grant_ref"], "process": values["recorded_process"], "result": result_ref}
    job = {key: ids[key] for key in ("job_id", "problem_id", "configuration_id")}
    plan = {"series_id": ids["series_id"], "jobs": [job],
        "project_binding": {"project_id": str(uuid4()), "relative_root": "runs/native-series"}}
    state = {"jobs": [{"job_id": ids["job_id"], "status": attempt["execution_status"], "attempts": [attempt]}]}
    monkeypatch.setattr(controller, "loaded_source", lambda: ({}, {}, {}))
    if terminal:
        monkeypatch.setattr(controller, "verify_result", lambda *_: {"execution_status": "completed", "execution_stage": "solver"})
    return controller, root, plan, state


def test_resume_rejects_foreign_status_pid_before_any_group_probe(tmp_path, monkeypatch):
    controller, root, plan, state = controller_fixture(tmp_path, monkeypatch)
    state["jobs"][0]["attempts"][0]["process"] = {
        **state["jobs"][0]["attempts"][0]["process"], "pid": 999, "pgid": 999, "sid": 999}
    before = copy.deepcopy(state)
    def forbidden(*_):
        raise AssertionError("An unverified status PID must not authorize a group probe")
    monkeypatch.setattr(controller, "group_status", forbidden)
    with pytest.raises(controller.RecoveryBlockedError, match="launch chain"):
        controller._recover(root, plan, state, None)
    assert state == before


def test_even_a_terminal_record_cannot_authorize_overlap_with_a_live_group(tmp_path, monkeypatch):
    controller, root, plan, state = controller_fixture(tmp_path, monkeypatch, terminal=True)
    monkeypatch.setattr(controller, "group_status", lambda _: "alive")
    with pytest.raises(controller.RecoveryBlockedError, match="terminal attempt"):
        controller._recover(root, plan, state, None)


def test_verified_ended_terminal_attempt_is_preserved(tmp_path, monkeypatch):
    controller, root, plan, state = controller_fixture(tmp_path, monkeypatch, terminal=True)
    before = copy.deepcopy(state)
    monkeypatch.setattr(controller, "group_status", lambda _: "dead")
    controller._recover(root, plan, state, None)
    assert state == before
