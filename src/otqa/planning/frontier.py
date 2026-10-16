"""Certified complete-policy selection, with root-only progress admission."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import math
from collections.abc import Callable

from .dominance import binary_integer, certified_projection
from .models import PolicyOption, option_identity


@dataclass(frozen=True, slots=True)
class CombinationSelection:
    selected: tuple[PolicyOption, ...] | None
    best_progress_witness: tuple[PolicyOption, ...]


def pareto_options(options, observe: Callable[[str, object], None] | None = None):
    """Retain coordinate/identity nondominance, without local admission."""
    records = [(binary_integer(item.expected_queries), binary_integer(item.expected_terminal_loss),
                option_identity(item), item) for item in options]

    def report(record, keep, witness):
        observe("frontier_projection", ("pruning_decision", "child_options", None, record[3], keep,
            "certified_nondominated" if keep else "certified_dominance", witness[3] if witness else None))

    return tuple(item[3] for item in certified_projection(records, report if observe else None))


def select_frontiers(candidate_count, probabilities, raw_options, *, minimum=None,
                     observe=None, child_observers=None) -> CombinationSelection:
    """Select complete admitted plans and retain a maximum-gain witness.

    Raw child options survive until the all-negative test. Negative native gains
    with disabled admission cannot use cost/loss dominance. That exceptional path
    enumerates the unpruned product, without clamping any score.
    """
    if len(probabilities) != len(raw_options) or not raw_options:
        raise ValueError("probability and frontier counts differ or are empty")
    for probability, options in zip(probabilities, raw_options, strict=True):
        if not math.isfinite(probability) or not 0.0 < probability <= 1.0:
            raise ValueError("frontiers require positive finite probabilities")
        if not options:
            raise RuntimeError("missing positive-probability child policy frontier")
        for option in options:
            if not math.isfinite(option.expected_terminal_loss) or option.expected_terminal_loss < 0.0 or (
                not math.isfinite(option.expected_queries) or option.expected_queries < 0.0
            ):
                raise ValueError("invalid child policy coordinates")
    if minimum is not None and (isinstance(minimum, bool) or not math.isfinite(minimum) or minimum < 0.0):
        raise ValueError("minimum progress must be finite and nonnegative or None")

    minimum_loss = math.fsum(p * min(option.expected_terminal_loss for option in options)
                            for p, options in zip(probabilities, raw_options, strict=True))
    negative_only = minimum is None and float(candidate_count) - minimum_loss < 0.0
    if negative_only:
        combinations = product(*raw_options)
        if observe:
            observe("frontier_projection", ("negative_gain_exhaustive",))
    else:
        frontiers = tuple(pareto_options(options,
            child_observers[index] if child_observers else observe)
            for index, options in enumerate(raw_options))
        # Prefix certificates sum the native rounded products exactly.
        prefixes = [(0, 0, (), ())]
        for index, options in enumerate(frontiers[:-1]):
            terms = [(binary_integer(probabilities[index] * item.expected_queries),
                      binary_integer(probabilities[index] * item.expected_terminal_loss),
                      option_identity(item), item) for item in options]
            expanded = [(prefix[0] + term[0], prefix[1] + term[1],
                         prefix[2] + (term[2],), prefix[3] + (term[3],))
                        for prefix in prefixes for term in terms]

            def report(record, keep, witness, index=index):
                observe("frontier_projection", ("pruning_decision", "weighted_combinations", index,
                    record[3], keep, "certified_nondominated" if keep else "certified_dominance",
                    witness[3] if witness else None))

            prefixes = certified_projection(expanded, report if observe else None)
        combinations = (prefix[3] + (last,) for prefix in prefixes for last in frontiers[-1])

    selected = witness = None
    selected_key = witness_key = None
    for chosen in combinations:
        loss = math.fsum(p * item.expected_terminal_loss for p, item in zip(probabilities, chosen, strict=True))
        cost = 1.0 + math.fsum(p * item.expected_queries for p, item in zip(probabilities, chosen, strict=True))
        gain = float(candidate_count) - loss
        key = (-gain / cost, cost, tuple(option_identity(item) for item in chosen))
        # A maximum-progress witness is tied by policy identity, not by rate.
        # Cost/loss dominance is unsafe for negative-rate tie selection, even
        # when such a witness will correctly fail an active threshold.
        progress_key = (-gain, key[2])
        if witness_key is None or progress_key < witness_key:
            witness, witness_key = chosen, progress_key
        if (minimum is None or gain > minimum) and (selected_key is None or key < selected_key):
            selected, selected_key = chosen, key
    if observe:
        observe("combination_choice", (probabilities, selected, selected_key, witness, witness_key))
    assert witness is not None
    return CombinationSelection(selected, witness)


def combine_frontiers(candidate_count, probabilities, frontiers, observe=None):
    """Threshold-disabled pure API retained for analytical callers."""
    result = select_frontiers(candidate_count, probabilities, frontiers, observe=observe)
    assert result.selected is not None
    return result.selected
