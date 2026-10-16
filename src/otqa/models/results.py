"""Immutable solver states, results, counts, and synchronous event payloads."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias

from .core import AnsweredQuery, Query
from .execution import ExecutionCursor, PendingPlanningCycle, PlanningAttempt, PlanningCycle

from .planning import PlanningDecision


@dataclass(frozen=True, slots=True)
class StateAnalysis:
    answered_total: int
    candidate_indices: tuple[int, ...]
    candidate_volumes: tuple[tuple[int, float], ...]
    candidate_volume_shares: tuple[tuple[int, float], ...]
    feasible: bool = True

    @property
    def candidate_count(self) -> int:
        return len(self.candidate_indices)


@dataclass(frozen=True, slots=True)
class QueryCounts:
    initial_answers: int
    dispatched_new: int
    answered_new: int
    answered_total: int

    def __post_init__(self) -> None:
        values = (self.initial_answers, self.dispatched_new, self.answered_new, self.answered_total)
        if any(type(value) is not int or value < 0 for value in values):
            raise ValueError('query counts must be nonnegative integers')
        if self.answered_new > self.dispatched_new or self.answered_total != self.initial_answers + self.answered_new:
            raise ValueError('inconsistent query counts')


@dataclass(frozen=True, slots=True)
class QueryRecord:
    query: Query
    answer: Literal['<', '>', '=']
    planning: PlanningDecision
    before: StateAnalysis
    after: StateAnalysis
    cycle: PlanningCycle | None = None


@dataclass(frozen=True, slots=True)
class SolveResult:
    solved: bool
    exactly_solved: bool
    termination_reason: Literal['exact_single_candidate', 'volume_confidence', 'no_query', 'max_questions', 'insufficient_expected_progress']
    selected_candidate_index: int | None
    selected_candidate_volume: float | None
    selected_candidate_volume_share: float | None
    final_state: StateAnalysis
    answers: tuple[AnsweredQuery, ...]
    queries: tuple[QueryRecord, ...]
    query_counts: QueryCounts
    execution_cursor: ExecutionCursor | None = None
    planning_cycles: tuple[PlanningCycle, ...] = ()
    continuation_binding: tuple[str, str] | None = None


@dataclass(frozen=True, slots=True)
class PartialContext:
    last_state: StateAnalysis | None
    answers: tuple[AnsweredQuery, ...]
    queries: tuple[QueryRecord, ...]
    query_counts: QueryCounts
    open_query: Query | None
    execution_cursor: ExecutionCursor | None = None
    planning_cycles: tuple[PlanningCycle, ...] = ()
    pending_cycle: PendingPlanningCycle | None = None
    continuation_binding: tuple[str, str] | None = None


@dataclass(frozen=True, slots=True)
class StateAnalyzed:
    state: StateAnalysis
    execution_cursor: ExecutionCursor | None = None


@dataclass(frozen=True, slots=True)
class PlanningAttemptStarted:
    cursor: ExecutionCursor
    state: StateAnalysis
    attempt_index: int
    requested_depth: int


@dataclass(frozen=True, slots=True)
class PlanningAttemptCompleted:
    cursor: ExecutionCursor
    state: StateAnalysis
    attempt_index: int
    attempt: PlanningAttempt


@dataclass(frozen=True, slots=True)
class PlanningResolved:
    cycle: PlanningCycle
    state: StateAnalysis


@dataclass(frozen=True, slots=True)
class QueryPlanned:
    planning: PlanningDecision
    state: StateAnalysis
    cycle: PlanningCycle | None = None


@dataclass(frozen=True, slots=True)
class QueryDispatched:
    query: Query
    query_counts: QueryCounts


@dataclass(frozen=True, slots=True)
class AnswerReceived:
    answered_query: AnsweredQuery
    query_counts: QueryCounts
    execution_cursor: ExecutionCursor | None = None


@dataclass(frozen=True, slots=True)
class QueryCompleted:
    record: QueryRecord


@dataclass(frozen=True, slots=True)
class SolveFinished:
    result: SolveResult


SolverEvent: TypeAlias = (StateAnalyzed | PlanningAttemptStarted | PlanningAttemptCompleted | PlanningResolved
                         | QueryPlanned | QueryDispatched | AnswerReceived | QueryCompleted | SolveFinished)
