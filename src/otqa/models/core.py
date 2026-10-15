"""Immutable mathematical inputs, independent of array and file libraries."""
from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Integral, Real
from typing import Literal, TypeAlias

from ..errors import InputValidationError, InvalidAnswerError

Answer: TypeAlias = Literal['<', '>', '=']


def finite_float(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise InputValidationError(f'{name} must be a real number')
    try:
        result = float(value)
    except (OverflowError, TypeError, ValueError) as exc:
        raise InputValidationError(f'{name} must be representable as binary64') from exc
    if not math.isfinite(result):
        raise InputValidationError(f'{name} must be finite')
    return result


def integer(value: object, *, name: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < minimum:
        raise InputValidationError(f'{name} must be an integer >= {minimum}')
    return int(value)


def validate_answer(value: object) -> Answer:
    if not isinstance(value, str) or value not in ('<', '>', '='):
        raise InvalidAnswerError('answer must be exactly one of <, >, =')
    return value


@dataclass(frozen=True, slots=True)
class Problem:
    """An owned matrix in original row/column order; no normalization."""

    alternatives: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        try:
            if isinstance(self.alternatives, (str, bytes)):
                raise TypeError('matrix is a string')
            rows = tuple(tuple(finite_float(value, name='matrix entry') for value in row)
                         for row in self.alternatives)
        except (TypeError, OverflowError) as exc:
            raise InputValidationError('alternatives must be a rectangular numerical matrix') from exc
        if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
            raise InputValidationError('alternatives must have at least one row and column and be rectangular')
        if any(not 0.0 <= value <= 1.0 for row in rows for value in row):
            raise InputValidationError('matrix entries must lie in [0, 1]')
        object.__setattr__(self, 'alternatives', rows)

    @property
    def alternative_count(self) -> int:
        return len(self.alternatives)

    @property
    def objective_count(self) -> int:
        return len(self.alternatives[0])


@dataclass(frozen=True, slots=True)
class Query:
    goal_index_a: int
    goal_index_b: int
    value: float

    def __post_init__(self) -> None:
        a = integer(self.goal_index_a, name='goal_index_a')
        b = integer(self.goal_index_b, name='goal_index_b')
        value = finite_float(self.value, name='query value')
        if a == b or value < 0.0:
            raise InputValidationError('query needs distinct indices and a nonnegative value')
        object.__setattr__(self, 'goal_index_a', a)
        object.__setattr__(self, 'goal_index_b', b)
        object.__setattr__(self, 'value', value)

    def validate_for(self, problem: Problem) -> None:
        if max(self.goal_index_a, self.goal_index_b) >= problem.objective_count:
            raise InputValidationError('query index outside problem objectives')


@dataclass(frozen=True, slots=True)
class AnsweredQuery:
    query: Query
    answer: Answer

    def __post_init__(self) -> None:
        if not isinstance(self.query, Query):
            raise InputValidationError('answered query requires a Query')
        validate_answer(self.answer)
