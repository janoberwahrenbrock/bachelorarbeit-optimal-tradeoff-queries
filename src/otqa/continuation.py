"""Bound SDK continuation values; no durable-storage or numerical claims."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .config import AlgorithmPolicy, VolumeConfidenceStop
from .errors import InputValidationError
from .execution import validate_cursor
from .models.core import AnsweredQuery, Problem
from .models.execution import ExecutionCursor
from .models.results import PartialContext, SolveResult


def _problem_identity(problem: Problem) -> tuple:
    return tuple(tuple(value.hex() for value in row) for row in problem.alternatives)


def _policy_identity(policy: AlgorithmPolicy) -> tuple:
    stopping = ('volume_confidence', policy.stopping.threshold.hex()) if isinstance(policy.stopping, VolumeConfidenceStop) else ('single_candidate',)
    threshold = policy.min_expected_progress
    return (policy.query_strategy, policy.depth, policy.higher_depth_query_source,
            policy.grid_size, policy.planning_evaluation, stopping, policy.horizon_execution,
            None if threshold is None else threshold.hex())


def continuation_binding(problem: Problem, policy: AlgorithmPolicy) -> tuple[str, str]:
    """Path-independent binary64 identities for an in-memory result binding."""
    def bound(value):
        return hashlib.sha256(json.dumps(value, separators=(',', ':'), ensure_ascii=True).encode('ascii')).hexdigest()
    return bound(_problem_identity(problem)), bound(_policy_identity(policy))


@dataclass(frozen=True, slots=True)
class SolveContinuation:
    """Explicit accepted history and phase bound to immutable problem and policy.

    A manually constructed cursor is a caller declaration, not evidence of an
    earlier run. Native files add their own verified durable origin proof.
    """

    problem: Problem
    policy: AlgorithmPolicy
    answers: tuple[AnsweredQuery, ...]
    execution_cursor: ExecutionCursor
    contract_version: int = 2

    def __post_init__(self) -> None:
        if not isinstance(self.problem, Problem) or not isinstance(self.policy, AlgorithmPolicy):
            raise InputValidationError('continuation requires a Problem and AlgorithmPolicy')
        if type(self.contract_version) is not int or self.contract_version != 2:
            raise InputValidationError('unsupported SDK continuation contract')
        try:
            answers = tuple(self.answers)
        except TypeError as exc:
            raise InputValidationError('continuation answers must be a sequence') from exc
        for answer in answers:
            if not isinstance(answer, AnsweredQuery):
                raise InputValidationError('continuation answers must be AnsweredQuery values')
            answer.query.validate_for(self.problem)
        object.__setattr__(self, 'answers', answers)
        validate_cursor(self.policy, self.execution_cursor, len(answers))

    def validate_for(self, problem: Problem, policy: AlgorithmPolicy) -> None:
        if _problem_identity(problem) != _problem_identity(self.problem):
            raise InputValidationError('continuation belongs to a different mathematical problem')
        if _policy_identity(policy) != _policy_identity(self.policy):
            raise InputValidationError('continuation belongs to a different algorithm policy')
        validate_cursor(policy, self.execution_cursor, len(self.answers))

    @classmethod
    def from_result(cls, problem: Problem, policy: AlgorithmPolicy,
                    result: SolveResult | PartialContext) -> SolveContinuation:
        return continuation_from_result(problem, policy, result)


def continuation_from_result(problem: Problem, policy: AlgorithmPolicy,
                             result: SolveResult | PartialContext) -> SolveContinuation:
    """Export accepted in-memory state, including an answered incomplete record.

    This helper never promises that an external recorder durably committed the
    same state. An unanswered dispatch is deliberately not repeated for callers.
    """
    if not isinstance(result, (SolveResult, PartialContext)):
        raise InputValidationError('continuation export needs a solver result or partial context')
    counts = result.query_counts
    if counts.answered_new != counts.dispatched_new:
        raise InputValidationError('an unanswered dispatch prevents automatic continuation export')
    if counts.answered_total != len(result.answers) or result.execution_cursor is None:
        raise InputValidationError('solver state lacks an accepted-history execution cursor')
    if result.continuation_binding != continuation_binding(problem, policy):
        raise InputValidationError('solver state was produced for a different problem or policy')
    return SolveContinuation(problem, policy, result.answers, result.execution_cursor)
