"""Actual installed public CLI continuation/export/warm-start acceptance.

This control uses an already qualified installed wheel and creates only new
project-local inputs and native runs. It is a functional control, not a runtime
comparison or an independent recertification of geometry.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from otqa.runtime.codec import encode, utc_now
from otqa.runtime.documents import file_ref, resolve_ref
from otqa.runtime.project import load_project_context
from otqa.runtime.source import loaded_source
from otqa.runtime.storage import create_directory, publish_json
from otqa.runtime.validation import verify_result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--execution-profile", type=Path, required=True)
    parser.add_argument("--output-id", required=True)
    args = parser.parse_args()
    context = load_project_context(args.project_root)
    root = context.project_root
    inputs = root / "inputs" / args.output_id
    outputs = root / "runs" / args.output_id
    create_directory(context, inputs, namespace="inputs")
    create_directory(context, outputs)
    source_before = loaded_source()
    receipt = {"started_at_utc": utc_now(), "source": source_before[0],
               "scope": "Installed public CLI only; not a timing comparison", "commands": [], "passed": False}

    def command(*arguments, expected=(0,)):
        invocation = [str(Path(sys.executable).with_name("otqa")), "--project-root", str(root),
                      *map(str, arguments)]
        started = time.perf_counter()
        result = subprocess.run(invocation, cwd=outputs, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, check=False)
        record = {"arguments": invocation, "returncode": result.returncode,
                  "wall_seconds": time.perf_counter() - started,
                  "stdout": result.stdout, "stderr": result.stderr}
        receipt["commands"].append(record)
        if result.returncode not in expected:
            raise RuntimeError(f"Native command failed: {result.returncode}: {result.stdout} {result.stderr}")
        return json.loads(result.stdout)

    problem = {"schema_version": 1, "problem_id": "continuation-control", "alternative_ids": ["left", "right", "middle"],
               "objective_ids": ["g0", "g1"], "alternatives": [[1., 0.], [0., 1.], [.6, .6]]}
    oracle = {"schema_version": 1, "problem_id": problem["problem_id"], "target_weights": [.9, .1]}
    config = {"schema_version": 2, "configuration_id": "continuation-countdown2",
        "algorithm": {"query_strategy": "fixed", "depth": 2, "higher_depth_query_source": "both", "grid_size": 5,
            "planning_evaluation": "candidate_count", "stopping": {"rule": "single_candidate"},
            "horizon_execution": "countdown", "min_expected_progress": None},
        "budget": {"max_queries": None},
        "execution": {"workers": 8, "native_threads": 1, "start_method": "forkserver",
            "cache_policy_id": "bounded_v1", "case_timeout_seconds": None},
        "recording": {"durability": "per_answer", "trace_level": "standard", "profile": False,
            "telemetry_failure_policy": "continue"}}
    try:
        for name, document, kind in (("problem", problem, "problem"), ("oracle", oracle, "oracle"), ("config", config, "config")):
            publish_json(context, inputs / f"{name}.json", document, kind=kind, namespace="inputs")
        common = ["solve", "--source-root", root, "--problem", inputs / "problem.json", "--config", inputs / "config.json",
                  "--execution-profile", args.execution_profile, "--answers", "simulated", "--oracle", inputs / "oracle.json"]
        original_path = outputs / "origin"
        command(*common, "--output", original_path)
        original = json.loads((original_path / "result.json").read_text())
        original_manifest = json.loads((original_path / "manifest.json").read_text())
        verify_result(original_path / "result.json", original_path, original_manifest)
        assert original["solver_result"]["solved"] and original["query_counts"]["answered_total"] > 0
        exported = command("continuation", "export", "--result", original_path / "result.json",
                           "--source-root", original_path, "--output", inputs / "checkpoint")
        checkpoint_path = Path(exported["continuation_path"])
        checkpoint = json.loads(checkpoint_path.read_text())
        proof = checkpoint["origin_proof"]
        immutable_before = resolve_ref(root, proof["journal_prefix"]).read_bytes()
        resumed_path = outputs / "continued"
        command(*common, "--continuation", checkpoint_path, "--output", resumed_path)
        resumed = json.loads((resumed_path / "result.json").read_text())
        resumed_manifest = json.loads((resumed_path / "manifest.json").read_text())
        verify_result(resumed_path / "result.json", resumed_path, resumed_manifest)
        assert resumed["query_counts"]["initial_answers"] == original["query_counts"]["answered_total"]
        assert resumed["query_counts"]["answered_new"] == 0
        assert resumed["solver_result"]["selected_candidate_id"] == original["solver_result"]["selected_candidate_id"]
        assert resumed_manifest["execution_kind"] == "continuation"
        assert resumed_manifest["initial_execution_cursor"] == checkpoint["execution_cursor"]
        assert resumed_manifest["mathematical_input_sha256"] != original_manifest["mathematical_input_sha256"]
        assert resolve_ref(root, proof["journal_prefix"]).read_bytes() == immutable_before
        history = {"schema_version": 1, "problem_id": problem["problem_id"], "answers": checkpoint["answers"]}
        history_path = inputs / "history.json"
        publish_json(context, history_path, history, kind="answer_history", namespace="inputs")
        warm_path = outputs / "warm-start"
        command(*common, "--initial-answers", history_path, "--output", warm_path)
        warm_manifest = json.loads((warm_path / "manifest.json").read_text())
        warm = verify_result(warm_path / "result.json", warm_path, warm_manifest)
        assert warm_manifest["execution_kind"] == "warm_start"
        assert warm_manifest["initial_execution_cursor"] == {
            "answered_total": len(history["answers"]), "remaining_depth": config["algorithm"]["depth"]}
        assert warm["query_counts"]["answered_new"] == 0
        assert loaded_source() == source_before
        receipt.update({"passed": True, "finished_at_utc": utc_now(),
            "original_result": file_ref(original_path / "result.json", root),
            "continuation": file_ref(checkpoint_path, root),
            "continued_result": file_ref(resumed_path / "result.json", root),
            "warm_start_result": file_ref(warm_path / "result.json", root),
            "verified": ["Actual qualified native runs", "Public CLI immutable checkpoint export", "Native materialized proof import",
                "Bound source/environment", "Preserved explicit cursor", "No repeated provider question", "Warm-start full depth"]})
    except BaseException as error:
        receipt.update({"finished_at_utc": utc_now(), "error": {"type": type(error).__name__, "message": str(error)}})
        raise
    finally:
        publish_json(context, outputs / "acceptance.json", receipt)
    print(encode({"passed": True, "receipt": str(outputs / "acceptance.json")}).decode().strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
