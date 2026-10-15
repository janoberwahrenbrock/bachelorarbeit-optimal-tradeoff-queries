import json
import subprocess
import sys
from uuid import uuid4

from otqa.runtime.codec import encode


def test_cli_help_and_import_are_lightweight(tmp_path):
    run = subprocess.run([sys.executable, "-c", "import sys,otqa.cli;assert 'numpy' not in sys.modules and 'scipy' not in sys.modules"],
                         cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    help_run = subprocess.run([sys.executable, "-m", "otqa", "--help"], cwd=tmp_path, capture_output=True, text=True)
    assert help_run.returncode == 0
    assert "benchmark" in help_run.stdout and "dataset" in help_run.stdout


def test_cli_does_not_guess_a_project_from_a_parent(tmp_path):
    (tmp_path / "otqa-project.json").write_bytes(encode({"schema_version": 1, "project_kind": "otqa_project", "project_id": str(uuid4())}))
    nested = tmp_path / "nested"
    nested.mkdir()
    run = subprocess.run([sys.executable, "-m", "otqa", "benchmark", "status", "--series", "missing"], cwd=nested, capture_output=True, text=True)
    assert run.returncode == 2
    diagnostic = json.loads(run.stdout)
    assert diagnostic["error"]["code"] == "invalid_input"
    assert "otqa-project.json" in diagnostic["error"]["message"]
    assert not (tmp_path / "runs").exists()
