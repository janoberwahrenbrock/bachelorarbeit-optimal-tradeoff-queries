"""Exact binary64 sum certificates, separate from native score arithmetic."""
from __future__ import annotations

import math


def binary_integer(value: float) -> int:
    """Return the numerator over the shared exact denominator 2**1074."""
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("a dominance coordinate must be finite")
    numerator, denominator = value.as_integer_ratio()
    return numerator << (1074 - (denominator.bit_length() - 1))


def certified_projection(records, report=None):
    """Project (exact_cost, exact_loss, identity, payload) in O(m log m).

An earlier point is a witness only when all three coordinates are <=.
The identity condition protects native-score ties after later rounding.
"""
    ordered = sorted(records, key=lambda item: item[:3])
    identities = sorted({item[2] for item in ordered})
    ranks = {identity: index + 1 for index, identity in enumerate(identities)}
    minima = [None] * (len(identities) + 1)
    retained = []
    for record in ordered:
        rank = ranks[record[2]]
        witness, cursor = None, rank
        while cursor:
            other = minima[cursor]
            if other is not None and (witness is None or other[1] < witness[1]):
                witness = other
            cursor -= cursor & -cursor
        keep = witness is None or witness[1] > record[1]
        if keep:
            retained.append(record)
            cursor = rank
            while cursor < len(minima):
                if minima[cursor] is None or record[1] < minima[cursor][1]:
                    minima[cursor] = record
                cursor += cursor & -cursor
        if report is not None:
            report(record, keep, None if keep else witness)
    return retained
