"""Answer providers remain outside the planner and never supply it a winner."""
from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from ..errors import InputValidationError
from ..models import Answer, AnsweredQuery, Query
from ..models.core import finite_float, validate_answer


@dataclass(frozen=True, slots=True)
class SimulatedAnswers:
    weights: tuple[float, ...]

    def __post_init__(self) -> None:
        weights = tuple(finite_float(value, name='target weight') for value in self.weights)
        if not weights or min(weights) < 0 or not math.isfinite(sum(weights)) or sum(weights) <= 0:
            raise InputValidationError('weights must be nonnegative with a finite positive sum')
        object.__setattr__(self, 'weights', weights)

    def __call__(self, query: Query) -> Answer:
        if max(query.goal_index_a, query.goal_index_b) >= len(self.weights):
            raise InputValidationError('query outside target weights')
        left = self.weights[query.goal_index_a]
        right = query.value * self.weights[query.goal_index_b]
        return '<' if left < right else '>' if left > right else '='


class ReplayAnswers:
    """Consume exactly the stored mathematical query identities in order."""

    def __init__(self, answers: Sequence[AnsweredQuery]):
        self._answers = tuple(answers)
        if any(not isinstance(item, AnsweredQuery) for item in self._answers):
            raise InputValidationError('replay requires AnsweredQuery values')
        self._index = 0

    def __call__(self, query: Query) -> Answer:
        if self._index >= len(self._answers):
            raise InputValidationError('replay answer script exhausted')
        expected = self._answers[self._index]
        if (query.goal_index_a, query.goal_index_b, query.value.hex()) != (
                expected.query.goal_index_a, expected.query.goal_index_b, expected.query.value.hex()):
            raise InputValidationError('replay query differs from planned query')
        self._index += 1
        return expected.answer

    @property
    def consumed(self) -> int:
        return self._index


class InteractiveAnswers:
    def __init__(self, read: Callable[[str], str] = input):
        self._read = read

    def __call__(self, query: Query) -> Answer:
        return validate_answer(self._read(
            f'w[{query.goal_index_a}] ? {query.value!r} * w[{query.goal_index_b}] (<, >, =): '))


__all__ = ['SimulatedAnswers', 'ReplayAnswers', 'InteractiveAnswers']
