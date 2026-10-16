"""Public invocation contracts keep mathematical inputs and start kinds explicit."""
from pathlib import Path
from uuid import uuid4
import json

import pytest

from otqa.cli.main import main, parser
from otqa.runtime.codec import encode


def test_solve_warm_start_and_continuation_are_mutually_exclusive():
    arguments = ["solve", "--source-root", ".", "--problem", "p.json", "--config", "c.json",
                 "--execution-profile", "profile.json", "--output", "runs/new", "--answers", "simulated",
                 "--initial-answers", "answers.json", "--continuation", "continuation.json"]
    with pytest.raises(SystemExit) as failure:
        parser().parse_args(arguments)
    assert failure.value.code == 2


def test_continuation_export_has_no_implicit_solver_overrides():
    args = parser().parse_args(["continuation", "export", "--result", "runs/old/result.json",
                               "--output", "inputs/new"])
    assert args.result == Path("runs/old/result.json")
    assert args.output == Path("inputs/new")
    assert args.source_root is None
    assert not hasattr(args, "depth") and not hasattr(args, "workers")


def _historical_configuration():
    return {"schema_version": 1, "configuration_id": "historical",
        "algorithm": {"query_strategy": "fixed", "depth": 2, "higher_depth_query_source": "both",
            "grid_size": 5, "planning_evaluation": "candidate_count", "stopping": {"rule": "single_candidate"}},
        "budget": {"max_queries": None},
        "execution": {"workers": 1, "native_threads": 1, "start_method": "forkserver",
            "cache_policy_id": "bounded_v1", "case_timeout_seconds": None},
        "recording": {"durability": "per_answer", "trace_level": "standard", "profile": False,
            "telemetry_failure_policy": "continue"}}


def _project(tmp_path):
    (tmp_path / "otqa-project.json").write_bytes(encode({"schema_version": 1,
        "project_kind": "otqa_project", "project_id": str(uuid4())}))
    return tmp_path


@pytest.mark.parametrize("value,expected", [(None, None), ("0.001", 0.001), ("none", None), ("0", 0.0)])
def test_explicit_configuration_conversion_writes_new_current_input(tmp_path, capsys, value, expected):
    project = _project(tmp_path)
    original = project / "historical.json"
    original.write_bytes(encode(_historical_configuration()))
    before = original.read_bytes()
    output = project / "inputs" / "converted.json"
    arguments = ["--project-root", str(project), "config", "convert", "--input", str(original),
                 "--output", str(output)]
    if value is not None:
        arguments.extend(["--min-expected-progress", value])
    assert main(arguments) == 0
    result = json.loads(output.read_text())
    assert result["schema_version"] == 2
    assert result["algorithm"]["min_expected_progress"] == expected
    assert result["algorithm"]["horizon_execution"] == "receding"
    assert original.read_bytes() == before
    assert main(arguments) != 0
    assert json.loads(capsys.readouterr().out.splitlines()[-1])["error"]


def test_old_countdown_requires_explicit_semantic_choice(tmp_path, capsys):
    project = _project(tmp_path)
    old = _historical_configuration()
    old["algorithm"]["horizon_execution"] = "countdown"
    original = project / "old.json"
    original.write_bytes(encode(old))
    output = project / "inputs" / "current.json"
    arguments = ["--project-root", str(project), "config", "convert", "--input", str(original),
                 "--output", str(output)]
    assert main(arguments) == 2
    assert not output.exists()
    assert main([*arguments, "--accept-countdown-block-semantics"]) == 0
    assert json.loads(output.read_text())["algorithm"]["horizon_execution"] == "countdown"


@pytest.mark.parametrize("value", ["nan", "inf", "-1", "-inf"])
def test_invalid_conversion_threshold_never_publishes_new_input(tmp_path, capsys, value):
    project = _project(tmp_path)
    original = project / "old.json"
    original.write_bytes(encode(_historical_configuration()))
    output = project / "inputs" / "current.json"
    assert main(["--project-root", str(project), "config", "convert", "--input", str(original),
                 "--output", str(output), f"--min-expected-progress={value}"]) == 2
    assert not output.exists()
