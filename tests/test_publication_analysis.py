"""Offline reproduction compares values, not regenerated timestamp strings."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location("publication_compare", Path(__file__).parents[1] / "tools/publication/compare_analysis.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def sample():
    return {"study_id": "analytical-one", "independent_problems": 1, "primary_cells": 1,
            "repetitions": 1, "generated_at_utc": "original", "groups": [],
            "rows": [{"case_id": "p", "configuration_id": "c", "mode": "fixed", "grid": 3,
                      "solved": True, "quality": "correct", "queries": 2, "api_seconds": 1.5}]}


def test_generation_time_is_ignored():
    original = sample()
    reproduced = deepcopy(original)
    reproduced["generated_at_utc"] = "later"
    assert module.compare(original, reproduced)["passed"]


@pytest.mark.parametrize("field", ["queries", "api_seconds", "quality"])
def test_changed_measurement_rejected(field):
    original = sample()
    reproduced = deepcopy(original)
    reproduced["rows"][0][field] = "changed"
    with pytest.raises(ValueError, match="Scientific values"):
        module.compare(original, reproduced)


def test_duplicate_cell_rejected():
    original = sample()
    original["primary_cells"] = 2
    original["rows"] *= 2
    with pytest.raises(ValueError, match="duplicate"):
        module.compare(original, deepcopy(original))


def test_summary_uses_correct_solution_denominator():
    original = sample()
    failure = dict(original["rows"][0], case_id="unsolved", solved=False, quality="unknown", queries=0, api_seconds=0.1)
    original["rows"].append(failure)
    summary = module.summarize(original)[0]
    assert summary["cases"] == 2
    assert summary["correct"] == 1
    assert summary["mean_queries_correct"] == 2
    assert summary["mean_api_seconds_correct"] == 1.5
