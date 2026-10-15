"""Exact loss/cost frontiers for complete horizon-three child policies."""

from __future__ import annotations

import math
from collections.abc import Callable

from .models import PolicyOption, option_identity


def pareto_options(options: tuple[PolicyOption, ...] | list[PolicyOption]) -> tuple[PolicyOption, ...]:
    """Keep strictly improving loss in cost/loss/identity order, without epsilon."""
    retained: list[PolicyOption] = []
    lowest = math.inf
    for option in sorted(options, key=lambda item: (
        item.expected_queries, item.expected_terminal_loss, option_identity(item),
    )):
        if option.expected_terminal_loss < lowest:
            retained.append(option)
            lowest = option.expected_terminal_loss
    return tuple(retained)


def combine_frontiers(
    candidate_count: int,
    probabilities: tuple[float, ...],
    frontiers: tuple[tuple[PolicyOption, ...], ...],
    observe: Callable[[str, object], None] | None = None,
) -> tuple[PolicyOption, ...]:
    """Choose the ratio of expectations, preserving ordered product reductions.

    A locally maximal child rate is insufficient. Dominance is valid only for
    the weighted loss/cost pairs of complete policies. Positive answer slots
    retain their original ordering at every accumulation.
    """
    if len(probabilities) != len(frontiers):
        raise ValueError("probability and frontier counts differ")
    combinations: list[tuple[PolicyOption, ...]] = [()]
    for index, frontier in enumerate(frontiers):
        if not frontier:
            raise RuntimeError("missing positive-probability child policy frontier")
        expanded = [prefix + (option,) for prefix in combinations for option in frontier]
        weighted = [(
            math.fsum(probabilities[i] * item.expected_queries for i, item in enumerate(chosen)),
            math.fsum(probabilities[i] * item.expected_terminal_loss for i, item in enumerate(chosen)),
            tuple(option_identity(item) for item in chosen),
            chosen,
        ) for chosen in expanded]
        combinations = []
        lowest = math.inf
        for _, loss, _, chosen in sorted(weighted, key=lambda item: item[:3]):
            if loss < lowest:
                combinations.append(chosen)
                lowest = loss
        if observe is not None:
            observe("frontier_projection", (index, tuple(weighted), tuple(combinations)))

    def key(chosen: tuple[PolicyOption, ...]) -> tuple:
        loss = math.fsum(p * item.expected_terminal_loss for p, item in zip(probabilities, chosen, strict=True))
        cost = 1.0 + math.fsum(p * item.expected_queries for p, item in zip(probabilities, chosen, strict=True))
        return (-(float(candidate_count) - loss) / cost, cost,
                tuple(option_identity(item) for item in chosen))

    if observe is None:
        chosen = min(combinations, key=key)
    else:
        # Keep the very key used by selection. Recomputing it for a trace
        # would manufacture another floating-point observation.
        iterator = iter(combinations)
        chosen = next(iterator)
        selected_key = key(chosen)
        for alternative in iterator:
            alternative_key = key(alternative)
            if alternative_key < selected_key:
                chosen, selected_key = alternative, alternative_key
        observe("combination_choice", (probabilities, chosen, selected_key))
    return chosen
