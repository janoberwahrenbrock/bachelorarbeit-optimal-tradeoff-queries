"""Compare published scientific results with a fresh offline raw-data analysis."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def compare(reference: dict, reproduced: dict) -> dict:
    """Ignore only generation timestamps; retain every measured value and binding."""
    for key in ("study_id", "independent_problems", "primary_cells", "repetitions"):
        if key not in reference or reference.get(key) != reproduced.get(key):
            raise ValueError(f"Study identity differs: {key}")
    left = {key: value for key, value in reference.items() if key != "generated_at_utc"}
    right = {key: value for key, value in reproduced.items() if key != "generated_at_utc"}
    if left.keys() != right.keys():
        raise ValueError("Analysis fields differ")
    for key in left:
        if left[key] != right[key]:
            raise ValueError(f"Scientific values or provenance differ: {key}")
    rows = reference.get("rows", [])
    identities = {(row["case_id"], row["configuration_id"]) for row in rows}
    if len(rows) != reference["primary_cells"] or len(identities) != len(rows):
        raise ValueError("Missing or duplicate problem/configuration cells")
    if len({row["case_id"] for row in rows}) != reference["independent_problems"]:
        raise ValueError("Independent problem count differs")
    return {"passed": True, "study_id": reference["study_id"],
            "primary_cells": len(rows), "independent_problems": reference["independent_problems"],
            "answers_checked": reference.get("answers_independently_checked"),
            "ignored_fields": ["generated_at_utc"], "solver_executed": False}


def summarize(result: dict) -> list[dict]:
    """Recompute condition means directly from individual saved measurements."""
    grouped = {}
    for row in result["rows"]:
        grouped.setdefault((row["mode"], row["grid"]), []).append(row)
    output = []
    for (mode, grid), rows in sorted(grouped.items()):
        correct = [row for row in rows if row["solved"] and row["quality"] == "correct"]
        output.append({"mode": mode, "grid": grid, "cases": len(rows), "correct": len(correct),
                       "mean_queries_correct": sum(row["queries"] for row in correct) / len(correct) if correct else None,
                       "mean_api_seconds_correct": sum(row["api_seconds"] for row in correct) / len(correct) if correct else None})
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--reproduced", type=Path)
    args = parser.parse_args()
    reference = json.loads(args.reference.read_text())
    value = compare(reference, json.loads(args.reproduced.read_text())) if args.reproduced else summarize(reference)
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
