"""Real Linux ownership/recovery faults for the installed-package qualifier.

Only the qualification harness injects these faults. Production has no bypass
flag, alternate solver, or fault-injection environment variable.
"""
from __future__ import annotations

import copy
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4


class InjectedControllerLoss(BaseException):
    """Leave the durable controller stage intact for the recovery reader."""


def _new_series(controls, name):
    from otqa.application import PlanRequest
    from otqa.experiments.controller import plan_suite
    from otqa.runtime.profiles import _candidate_resolver
    # The standalone qualification already created these fresh native inputs.
    assert (controls.root / "controls" / "suite.json").is_file()
    return plan_suite(PlanRequest(controls.context, controls.context.project_root,
        controls.root / "controls" / "suite.json", controls.root / "candidate-profile.json",
        controls.root / "linux" / name), resolver=_candidate_resolver).series_dir


def _expect_blocked(call):
    from otqa.runtime.supervisor import RecoveryBlockedError
    try:
        call()
    except RecoveryBlockedError as exc:
        return str(exc)
    raise AssertionError("Recovery started despite an unproven or live prior group")


def _file_hashes(root):
    from otqa.runtime.codec import digest
    return {path.relative_to(root).as_posix(): digest(path.read_bytes())
        for path in sorted(root.rglob("*")) if path.is_file()}


def _live_group(controls):
    from otqa.experiments.controller import _execute, _recover, load_series
    from otqa.runtime.codec import read_json
    from otqa.runtime.processes import group_status
    from otqa.runtime.profiles import _candidate_resolver
    from otqa.runtime.supervisor import supervise_attempt
    directory = _new_series(controls, "registered-loss")
    observations = {}

    def interrupted_supervisor(payload, *, context, on_phase):
        def phase(name, info):
            on_phase(name, info)
            if name != "registered":
                return
            assert group_status(info["process"]) == "alive"
            root, plan, state = load_series(directory, context=context, resolver=_candidate_resolver)
            before = copy.deepcopy(state)
            observations["group_block"] = _expect_blocked(lambda: _recover(root, plan, state, context))
            assert state == before
            observations["controller_lease_block"] = _expect_blocked(
                lambda: _execute(directory, context=context, resume=True, resolver=_candidate_resolver))
            observations["live_identity"] = info["process"]
            # The real shared supervisor closes its private release pipe. The
            # real CaseProcess sees EOF and must exit before any solver import.
            raise InjectedControllerLoss()
        return supervise_attempt(payload, context=context, on_phase=phase)

    try:
        with patch("otqa.experiments.controller.supervise_attempt", interrupted_supervisor):
            _execute(directory, context=controls.context, resume=False, resolver=_candidate_resolver)
    except InjectedControllerLoss:
        pass
    else:
        raise AssertionError("The registered-stage fault was not reached")
    state = read_json(directory / "state.json")
    attempt = state["jobs"][0]["attempts"][0]
    original = directory / attempt["directory"]
    assert group_status(attempt["process"]) == "dead"
    assert not (original / "manifest.json").exists() and not (original / "events.jsonl").exists()
    assert not (original / "start_grant.json").exists()
    assert len(state["jobs"][0]["attempts"]) == 1
    observations.update({"attempts_after_block": 1, "registered_child_ended_on_eof": True,
        "numerical_execution_started": False})
    controls.facts["linux_recovery_series"] = directory
    controls.facts["linux_original_attempt"] = original
    controls.facts["linux_original_files"] = _file_hashes(original)
    controls.facts["linux_live_observations"] = observations
    return observations


def _dead_retry(controls):
    from otqa.experiments.controller import _execute
    from otqa.runtime.codec import read_json
    from otqa.runtime.profiles import _candidate_resolver
    directory = controls.facts["linux_recovery_series"]
    outcome = _execute(directory, context=controls.context, resume=True, resolver=_candidate_resolver)
    assert outcome.exit_code == 0 and outcome.state["status"] == "completed"
    attempts = outcome.state["jobs"][0]["attempts"]
    assert len(attempts) == 2 and attempts[0]["run_id"] != attempts[1]["run_id"]
    assert attempts[0]["execution_status"] == "interrupted" and attempts[1]["execution_status"] == "completed"
    assert attempts[0]["directory"] != attempts[1]["directory"]
    original = read_json(directory / attempts[0]["directory"] / "result.json")
    retried = read_json(directory / attempts[1]["directory"] / "result.json")
    assert original["execution_stage"] == "bootstrap" and original["query_counts"]["answered_total"] == 0
    assert retried["solver_result"]["solved"] and retried["query_counts"]["answered_total"] == 1
    controls.facts["linux_retry_attempts"] = copy.deepcopy(attempts)
    return {"statuses": [item["execution_status"] for item in attempts],
        "run_ids": [item["run_id"] for item in attempts], "retry_queries": retried["query_counts"]}


def _unregistered(controls):
    from otqa.experiments.controller import _execute
    from otqa.runtime.codec import read_json
    from otqa.runtime.profiles import _candidate_resolver
    directory = _new_series(controls, "unregistered-gap")
    from otqa.runtime.supervisor import supervise_attempt
    def lose_before_spawn(payload, *, context, on_phase):
        def phase(name, info):
            on_phase(name, info)
            if name == "launching":
                raise InjectedControllerLoss()
        return supervise_attempt(payload, context=context, on_phase=phase)
    try:
        with patch("otqa.experiments.controller.supervise_attempt", lose_before_spawn):
            _execute(directory, context=controls.context, resume=False, resolver=_candidate_resolver)
    except InjectedControllerLoss:
        pass
    else:
        raise AssertionError("The reservation/spawn gap fault was not reached")
    state = read_json(directory / "state.json")
    attempt = state["jobs"][0]["attempts"][0]
    assert attempt["process"] is None and attempt["child_registration"] is None
    reason = _expect_blocked(lambda: _execute(directory, context=controls.context,
        resume=True, resolver=_candidate_resolver))
    assert len(read_json(directory / "state.json")["jobs"][0]["attempts"]) == 1
    # Exercise the real spawn -> registration window, including EOF, separately
    # from the durable controller reservation fixture above.
    eof = _before_registration_eof(controls)
    return {"uncertain_spawn_gap_block": reason, "attempts": 1, "real_child_eof": eof}


def _before_registration_eof(controls):
    from otqa.runtime.codec import utc_now
    from otqa.runtime.processes import _proc_fields, group_status, process_identity
    from otqa.runtime.profiles import _candidate_resolver
    from otqa.runtime.storage import publish_json
    from otqa.runtime.supervisor import prepare_standalone
    payload = prepare_standalone(controls.request("linux-before-registration-eof"), resolver=_candidate_resolver)
    directory = Path(payload["attempt_dir"])
    owner, nonce = uuid4().hex, uuid4().hex
    intent = {"schema_version": 1, "run_id": payload["run_id"], "attempt_id": payload["attempt_id"],
        "series_id": None, "job_id": None, "problem_id": payload["problem_id"],
        "configuration_id": payload["configuration_id"], "created_at_utc": utc_now(),
        "owner_token": owner, "nonce": nonce, "controller": process_identity(owner),
        "materialization_receipt": payload["materialization_receipt"]}
    publish_json(controls.context, directory / "launch_intent.json", intent, kind="launch_intent")
    publish_json(controls.context, directory / "case-request.json", payload)
    reader, writer = os.pipe()
    # This harness prefix pauses its actual, isolated child after exec and
    # before importing the installed CaseProcess. No production fault switch.
    script = "import os,signal,runpy;os.kill(os.getpid(),signal.SIGSTOP);runpy.run_module('otqa.runtime.case',run_name='__main__')"
    child = subprocess.Popen([sys.executable, "-c", script, "--request", str(directory / "case-request.json"),
        "--release-fd", str(reader)], pass_fds=(reader,), start_new_session=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.close(reader)
    try:
        deadline = time.monotonic() + 20
        while child.poll() is None and _proc_fields(child.pid)["state"] not in ("T", "t"):
            if time.monotonic() > deadline:
                raise AssertionError("The real pre-registration pause was not observed")
            time.sleep(.005)
        assert child.poll() is None and not (directory / "child_registration.json").exists()
        identity = process_identity(owner, child.pid)
        assert identity["pid"] == identity["pgid"] == identity["sid"]
        assert group_status(identity) == "alive"
        os.close(writer)
        writer = None
        os.kill(child.pid, signal.SIGCONT)
        stdout, stderr = child.communicate(timeout=20)
        assert child.returncode == 1 and group_status(identity) == "dead"
        assert (directory / "child_registration.json").is_file()
        assert not any((directory / name).exists() for name in ("start_grant.json", "manifest.json", "events.jsonl"))
        from otqa.runtime.codec import digest
        return {"stopped_before_registration": True, "actual_identity": identity,
            "registration_after_resume": True, "release_writer_closed_before_registration": True,
            "exit_code": child.returncode, "group_after_exit": "dead", "solver_started": False,
            "stdout_sha256": digest(stdout), "stderr_sha256": digest(stderr)}
    finally:
        if writer is not None:
            os.close(writer)
        if child.poll() is None:
            # Exact Popen child, whose only route is pre-release qualification.
            child.kill()
            child.communicate()


def _uncertain_start(controls):
    from otqa.experiments.controller import _execute
    from otqa.runtime.codec import read_json
    from otqa.runtime.profiles import _candidate_resolver
    from otqa.runtime.storage import publish_bytes
    from otqa.runtime.supervisor import supervise_attempt
    directory = _new_series(controls, "uncertain-start")
    def uncertain(payload, *, context, on_phase):
        def phase(name, info):
            on_phase(name, info)
            if name == "registered":
                # Simulate start-journal publication followed by a lost durable
                # cursor. The bytes are explicitly uncommitted fault evidence;
                # the recovery reader must not invent a successful start.
                publish_bytes(context, Path(payload["attempt_dir"]) / "events.jsonl", b'{"unconfirmed_start_fault":true}\n')
                raise InjectedControllerLoss()
        return supervise_attempt(payload, context=context, on_phase=phase)
    try:
        with patch("otqa.experiments.controller.supervise_attempt", uncertain):
            _execute(directory, context=controls.context, resume=False, resolver=_candidate_resolver)
    except InjectedControllerLoss:
        pass
    else:
        raise AssertionError("The unconfirmed-start fault was not reached")
    before = read_json(directory / "state.json")
    reason = _expect_blocked(lambda: _execute(directory, context=controls.context,
        resume=True, resolver=_candidate_resolver))
    after = read_json(directory / "state.json")
    assert before == after and len(after["jobs"][0]["attempts"]) == 1
    return {"blocked": reason, "unconfirmed_bytes_preserved": True, "new_attempts": 0}


def _retained(controls):
    from otqa.runtime.codec import read_json
    from otqa.runtime.documents import resolve_ref
    directory = controls.facts["linux_recovery_series"]
    attempts = read_json(directory / "state.json")["jobs"][0]["attempts"]
    assert attempts == controls.facts["linux_retry_attempts"]
    original = controls.facts["linux_original_attempt"]
    now = _file_hashes(original)
    for path, sha256 in controls.facts["linux_original_files"].items():
        assert now[path] == sha256
    results = [read_json(resolve_ref(directory, item["result"])) for item in attempts]
    assert [item["execution_status"] for item in results] == ["interrupted", "completed"]
    return {"retained_attempt_ids": [item["attempt_id"] for item in attempts],
        "original_immutable_files": len(controls.facts["linux_original_files"]),
        "interrupted_attempt_counted_as_success": False, "completed_attempts": 1}


def run_linux_control(controls, case: str) -> dict:
    if not os.path.isdir("/proc/self"):
        raise RuntimeError("Linux process evidence is unavailable")
    return {"live_group_blocks_resume": _live_group, "dead_group_fresh_retry": _dead_retry,
        "unregistered_eof": _unregistered, "uncertain_start_blocks_resume": _uncertain_start,
        "all_attempts_retained": _retained}[case](controls)
