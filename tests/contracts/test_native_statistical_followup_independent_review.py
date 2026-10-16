"""Independent prospective-gate checks; all artifacts/processes are synthetic.

These fixtures isolate the auditor and immutable-byte boundary. They do not
claim to be native schema-validated results and never call a solver or /proc.
"""
from copy import deepcopy
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
import json
from math import comb
from pathlib import Path

import pytest


SPEC = spec_from_file_location(
    "_native_followup_independent_review",
    Path(__file__).resolve().parents[2]
    / "tools/validation/compare_native_statistical_followup.py",
)
subject = module_from_spec(SPEC)
SPEC.loader.exec_module(subject)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, allow_nan=False) + "\n")


@pytest.mark.parametrize("successes", range(31))
def test_complete_tail_matches_independent_exact_enumeration(successes):
    expected = Fraction(sum(comb(30, k) for k in range(successes, 31)), 2**30)
    result = subject.classify([1.0] * successes + [1.05] * (30 - successes))
    assert subject.exact_tail(successes) == expected
    assert result["passed"] is (successes >= 23)
    assert Fraction(**result["exact_upper_tail"]) == expected


def campaign(tmp_path, monkeypatch):
    """Only aggregate-control tests replace native replay with a counted stub."""
    root = tmp_path
    directory = root / "runs/followup"
    conditions = subject.original.conditions()
    _, _, jobs = subject.schedule([c["condition_id"] for c in conditions])
    plan = {"purpose": "synthetic-pure-review", "conditions": conditions, "jobs": jobs}
    write(directory / "plan.json", plan)
    replayed = []
    monkeypatch.setattr(subject, "frozen", lambda *args: None)
    monkeypatch.setattr(subject, "check_job_binding", lambda *args: None)
    monkeypatch.setattr(
        subject, "raw_binding", lambda root, directory, plan, receipt: replayed.append(receipt["job"]["job_id"])
    )
    for job in jobs:
        receipt = {
            "job": job, "verified": True, "cli_returncode": 0, "reader_returncode": 0,
            "status": "completed", "solved": True, "fallbacks": 0,
            "quality": {"selected_correct": True, "actual_answers_correct": True},
            "cli_wall_seconds": 1.0 if job["variant"] == "old" or job["block"] <= 23 else 1.05,
            "api_seconds": 0.5, "case_seconds": 0.8, "answered_queries": 2,
            "mathematical_result": {"value": {"float_hex": "0x1.0000000000000p+0"}},
            "actual_sequence": [{"event_type": "query_completed", "query_id": "q1", "payload": {}}],
        }
        write(directory / "receipts" / (job["job_id"] + ".json"), receipt)
        write(directory / "bindings" / (job["job_id"] + ".json"), {})
        (directory / "cases" / job["job_id"]).mkdir(parents=True)
    return root, directory, plan, replayed


def test_audit_uses_all_720_fresh_calls_and_still_requires_end_proof(tmp_path, monkeypatch):
    root, directory, plan, replayed = campaign(tmp_path, monkeypatch)
    result = subject.audit(root, directory, plan)
    assert result["native_calls"] == len(replayed) == len(set(replayed)) == 720
    assert result["timing_pairs"] == 360
    assert result["all_calls_complete"] and result["all_statistical_conditions_passed"]
    assert all(c["strictly_below"] == 23 and c["ties_fail"] == 7 for c in result["conditions"])
    assert result["process_end_acceptance"] == "pending independent exact controller/group proof"
    assert result.get("accepted") is not True


def test_one_missing_fresh_call_cannot_be_filled_by_earlier_blocks(tmp_path, monkeypatch):
    root, directory, plan, _ = campaign(tmp_path, monkeypatch)
    (directory / "receipts" / (plan["jobs"][-1]["job_id"] + ".json")).unlink()
    with pytest.raises(ValueError, match="All720"):
        subject.audit(root, directory, plan)
    partial = subject.audit(root, directory, plan, complete=False)
    assert partial["native_calls"] == 719 and partial["timing_pairs"] == 359
    assert not partial["all_calls_complete"] and not partial["all_statistical_conditions_passed"]


@pytest.mark.parametrize("mutation", ["unplanned_receipt", "unplanned_case", "unplanned_binding", "math"])
def test_unplanned_or_mathematically_different_artifacts_prevent_acceptance(tmp_path, monkeypatch, mutation):
    root, directory, plan, _ = campaign(tmp_path, monkeypatch)
    if mutation == "unplanned_case":
        (directory / "cases" / "old-series-job").mkdir()
    elif mutation == "unplanned_binding":
        write(directory / "bindings" / "old-series-job.json", {})
    else:
        path = directory / "receipts" / (plan["jobs"][0]["job_id"] + ".json")
        receipt = json.loads(path.read_bytes())
        if mutation == "unplanned_receipt":
            receipt["job"]["job_id"] = "old-series-job"
            path = directory / "receipts" / "old-series-job.json"
        else:
            receipt["mathematical_result"]["value"]["float_hex"] = "0x1.0000000000001p+0"
        write(path, receipt)
    with pytest.raises(ValueError):
        subject.audit(root, directory, plan)


def byte_bound_job(tmp_path):
    """Minimal analytical bytes exercising binding, not native schema admission."""
    root, directory = tmp_path, tmp_path / "runs/followup"
    condition = subject.original.conditions()[0]
    job = {"job_id": "condition01-b1-new", "condition_id": "condition01", "block": 1, "variant": "new", "conditional": False}
    source = {"source_sha256": "fixture-source"}
    plan = {"conditions": [condition], "cases": subject.original.cases(), "source_probes": {"new": {"source": source}}}
    target = directory / "cases" / job["job_id"]
    config = subject.original.config(condition, "new")
    control = target / "inputs/control.json"
    write(control, {"fixture": "native-control-bytes"})
    manifest = {
        "source": source, "inputs": {"control": {"path": "inputs/control.json", "sha256": subject.sha(control)}},
        "execution_profile": None, "source_inventory": None, "launch_intent": None, "materialization_receipt": None,
        "process": {"boot_id": "fixture-boot", "pid": 101, "pgid": 101, "start_ticks": 42},
        **{"effective_" + name: config[name] for name in ("algorithm", "execution", "recording", "budget")},
    }
    write(target / "manifest.json", manifest)
    events = [{"event_type": "run_started", "payload": {"manifest_sha256": subject.sha(target / "manifest.json")}}]
    write(target / "events.jsonl", events[0])
    data = (target / "events.jsonl").read_bytes()
    solver = {"solved": True, "selected_candidate_id": "a2", "answered_queries": []}
    result = {
        "journal": {"path": "events.jsonl", "sha256": subject.original.digest(data), "bytes": len(data),
                    "valid_prefix_bytes": len(data), "valid_prefix_sha256": subject.original.digest(data), "uncommitted_suffix_bytes": 0},
        "execution_status": "completed", "solver_result": solver, "quality": {"status": "correct"},
        "query_counts": {"answered_new": 0},
    }
    write(target / "result.json", result)
    problem = {"alternative_ids": ["a0", "a1", "a2"]}
    write(directory / "inputs/analytic-g2-a3-problem.json", problem)
    receipt = {
        "job": job, "result_sha256": subject.sha(target / "result.json"), "journal_sha256": result["journal"]["sha256"],
        "actual_sequence": [], "mathematical_result": subject.original.mathematical(solver), "answered_queries": 0,
        "quality": subject.original.quality(plan["cases"][condition["case_id"]], problem, solver),
    }
    write(directory / "receipts" / (job["job_id"] + ".json"), receipt)
    subject.write_job_binding(root, directory, plan, receipt)
    return root, directory, plan, receipt, target


@pytest.mark.parametrize("changed", ["manifest", "receipt", "result", "journal", "control"])
def test_post_verification_byte_mutation_is_rejected(tmp_path, changed):
    root, directory, plan, receipt, target = byte_bound_job(tmp_path)
    subject.check_job_binding(root, directory, receipt)
    subject.raw_binding(root, directory, plan, receipt)
    paths = {
        "manifest": target / "manifest.json", "receipt": directory / "receipts" / (receipt["job"]["job_id"] + ".json"),
        "result": target / "result.json", "journal": target / "events.jsonl", "control": target / "inputs/control.json",
    }
    path = paths[changed]
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError):
        subject.check_job_binding(root, directory, receipt)
        subject.raw_binding(root, directory, plan, receipt)


def test_changed_process_identity_already_fails_journal_manifest_binding(tmp_path):
    root, directory, plan, receipt, target = byte_bound_job(tmp_path)
    manifest = json.loads((target / "manifest.json").read_bytes())
    manifest["process"]["pid"] = 999
    write(target / "manifest.json", manifest)
    with pytest.raises(ValueError, match="manifest"):
        subject.raw_binding(root, directory, plan, receipt)


def test_unreadable_existing_process_fails_closed_without_starting_anything(monkeypatch):
    class Entry:
        name = "123456789"

        def __truediv__(self, name):
            self.field = name
            return self

        def read_text(self):
            return "123456789 (python) " + " ".join(["S", "0", "123"] + ["0"] * 16 + ["42"])

        def read_bytes(self):
            raise PermissionError("unreadable existing cmdline")

    class Proc:
        def is_dir(self):
            return True

        def iterdir(self):
            return iter([Entry()])

    monkeypatch.setattr(subject, "Path", lambda path: Proc())
    with pytest.raises(ValueError, match="live/unknown"):
        subject.no_other_solvers()


def test_plan_does_not_accept_a_different_fresh_seed():
    conditions = subject.original.conditions()
    rounds, first, jobs = subject.schedule([c["condition_id"] for c in conditions])
    plan = {"conditions": conditions, "cases": subject.original.cases(), "seed": subject.SEED,
            "jobs": jobs, "round_condition_order": rounds, "first_variant_by_condition": first,
            "paired_blocks": list(range(1, 31)), "conditional_extra_blocks": [], "harness_sha256": subject.ORIGINAL_SHA,
            "source_probes": {"new": {"source": {"source_sha256": subject.NEW_SOURCE}}},
            "profiles": {"new": {"sha256": subject.NEW_PROFILE}}}
    subject.validate_plan(plan)
    changed = deepcopy(plan)
    changed["seed"] += 1
    with pytest.raises(ValueError, match="schedule"):
        subject.validate_plan(changed)
