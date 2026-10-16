"""Explicit algorithm policy, actual answer budget, and execution ownership."""
from __future__ import annotations

from dataclasses import dataclass, field
from multiprocessing.context import BaseContext
from typing import Literal

from .errors import InputValidationError
from .models.core import finite_float, integer


@dataclass(frozen=True, slots=True)
class SingleCandidateStop:
    """Accept only a state with one remaining candidate."""


@dataclass(frozen=True, slots=True)
class VolumeConfidenceStop:
    threshold: float

    def __post_init__(self) -> None:
        value = finite_float(self.threshold, name='confidence threshold')
        if not 0.0 < value <= 1.0:
            raise InputValidationError('confidence threshold must lie in (0, 1]')
        object.__setattr__(self, 'threshold', value)


@dataclass(frozen=True, slots=True)
class AlgorithmPolicy:
    query_strategy: Literal['fixed', 'reduction_per_query']
    depth: int
    higher_depth_query_source: Literal['grid', 'both']
    grid_size: int
    planning_evaluation: Literal['candidate_count', 'stop_aware']
    stopping: SingleCandidateStop | VolumeConfidenceStop
    horizon_execution: Literal['receding', 'countdown'] = 'receding'
    min_expected_progress: float | None = field(default=0.001, kw_only=True)

    def __post_init__(self) -> None:
        if self.query_strategy not in ('fixed', 'reduction_per_query'):
            raise InputValidationError('unknown query strategy')
        if self.horizon_execution not in ('receding', 'countdown'):
            raise InputValidationError('unknown horizon execution')
        if self.horizon_execution == 'countdown' and self.query_strategy != 'fixed':
            raise InputValidationError('countdown requires the fixed query strategy')
        depth = integer(self.depth, name='depth', minimum=1)
        grid_size = integer(self.grid_size, name='grid_size', minimum=1)
        if depth > 3:
            raise InputValidationError('depth must be 1, 2 or 3')
        if self.higher_depth_query_source not in ('grid', 'both'):
            raise InputValidationError('higher query source must be grid or both')
        if self.planning_evaluation not in ('candidate_count', 'stop_aware'):
            raise InputValidationError('unknown planning evaluation')
        if not isinstance(self.stopping, (SingleCandidateStop, VolumeConfidenceStop)):
            raise InputValidationError('stopping must be an explicit stop variant')
        object.__setattr__(self, 'depth', depth)
        object.__setattr__(self, 'grid_size', grid_size)
        if self.min_expected_progress is not None:
            minimum = finite_float(self.min_expected_progress, name='min_expected_progress')
            if minimum < 0.0:
                raise InputValidationError('min_expected_progress must be nonnegative or None')
            object.__setattr__(self, 'min_expected_progress', minimum)


@dataclass(frozen=True, slots=True)
class QueryBudget:
    max_queries: int | None = None

    def __post_init__(self) -> None:
        if self.max_queries is not None:
            object.__setattr__(self, 'max_queries', integer(self.max_queries, name='max_queries', minimum=1))


@dataclass(frozen=True, slots=True)
class SolverExecution:
    workers: int = 1
    multiprocessing_context: BaseContext | None = None
    cache_policy_id: Literal['bounded_v1'] = 'bounded_v1'

    def __post_init__(self) -> None:
        object.__setattr__(self, 'workers', integer(self.workers, name='workers', minimum=1))
        if self.multiprocessing_context is not None and not isinstance(self.multiprocessing_context, BaseContext):
            raise InputValidationError('multiprocessing_context must be a multiprocessing context')
        if self.cache_policy_id != 'bounded_v1':
            raise InputValidationError('unknown cache policy')
