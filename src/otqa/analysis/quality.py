"""Independent exact-rational oracle checks on stored binary64 inputs."""
from __future__ import annotations

from fractions import Fraction


def _fraction(value):
    return Fraction.from_float(float(value))


def evaluate_quality(problem: dict, oracle: dict | None, selected_id: str | None,
                     answers: list[dict]) -> dict:
    if oracle is None:
        return {"status": "not_selected" if selected_id is None else "unknown", "audit_status": "not_available",
                "true_winner_ids": [], "regret_fraction": None, "findings": []}
    weights = [_fraction(value) for value in oracle["target_weights"]]
    utilities = [sum((_fraction(value) * weight for value, weight in zip(row, weights)), Fraction()) for row in problem["alternatives"]]
    maximum = max(utilities)
    winners = [identifier for identifier, utility in zip(problem["alternative_ids"], utilities) if utility == maximum]
    findings = []
    for index, answer in enumerate(answers):
        difference = weights[answer["goal_index_a"]] - _fraction(answer["value"]) * weights[answer["goal_index_b"]]
        expected = "<" if difference < 0 else ">" if difference > 0 else "="
        if answer["answer"] != expected:
            findings.append(f"OracleConsistencyFinding at answer {index}: stored={answer['answer']}, exact={expected}")
    if selected_id is None:
        status, regret = "not_selected", None
    else:
        status = "correct" if selected_id in winners else "incorrect"
        regret = str(maximum - utilities[problem["alternative_ids"].index(selected_id)])
    return {"status": status, "audit_status": "failed" if findings else "passed", "true_winner_ids": winners,
            "regret_fraction": regret, "findings": findings}
