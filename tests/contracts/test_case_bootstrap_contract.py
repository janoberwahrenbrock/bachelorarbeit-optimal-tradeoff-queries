"""A real lightweight child must register before release using its own format."""
import os
import subprocess
import sys
from uuid import uuid4

from otqa.runtime.codec import encode, read_json, utc_now
from otqa.runtime.processes import process_identity
from otqa.runtime.schema import validate


def test_real_isolated_case_registers_v1_before_eof_without_starting_solver(tmp_path):
    (tmp_path / "otqa-project.json").write_bytes(encode({"schema_version": 1,
        "project_kind": "otqa_project", "project_id": str(uuid4())}))
    attempt = tmp_path / "runs" / "bootstrap"
    attempt.mkdir(parents=True)
    run_id, owner, nonce = str(uuid4()), uuid4().hex, uuid4().hex
    payload = {"project_root": str(tmp_path), "reference_root": str(attempt),
               "attempt_dir": str(attempt), "run_id": run_id, "attempt_id": "attempt0001"}
    intent = {"schema_version": 1, "run_id": run_id, "attempt_id": "attempt0001",
        "series_id": None, "job_id": None, "problem_id": "p", "configuration_id": "c",
        "created_at_utc": utc_now(), "owner_token": owner, "nonce": nonce,
        "controller": process_identity(uuid4().hex),
        "materialization_receipt": {"path": "materialization_receipt.json", "sha256": "0" * 64}}
    validate("launch_intent", intent)
    (attempt / "launch_intent.json").write_bytes(encode(intent))
    request = attempt / "case-request.json"
    request.write_bytes(encode(payload))
    read_fd, write_fd = os.pipe()
    try:
        child = subprocess.Popen([sys.executable, "-m", "otqa.runtime.case", "--request", str(request),
                                  "--release-fd", str(read_fd)], pass_fds=(read_fd,),
                                 start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.close(write_fd)
        write_fd = None
        try:
            stdout, stderr = child.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.communicate()
            raise
    finally:
        os.close(read_fd)
        if write_fd is not None:
            os.close(write_fd)
    assert child.returncode == 1, (stdout, stderr)
    registration = validate("child_registration", read_json(attempt / "child_registration.json"))
    assert registration["schema_version"] == 1
    assert registration["process"]["pid"] == child.pid
    assert registration["process"]["pgid"] == child.pid
    assert registration["nonce"] == nonce
    assert not (attempt / "manifest.json").exists()
    assert not (attempt / "events.jsonl").exists()
    assert not (attempt / "result.json").exists()
