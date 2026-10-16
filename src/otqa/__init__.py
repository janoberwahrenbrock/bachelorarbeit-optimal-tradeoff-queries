"""Optimal Tradeoff Queries: mathematical SDK with an independent runtime."""
from .api import solve
from .config import AlgorithmPolicy, QueryBudget, SingleCandidateStop, SolverExecution, VolumeConfidenceStop
from .continuation import SolveContinuation, continuation_from_result
from .models import Answer, AnsweredQuery, Problem, Query, SolveResult, SolverEvent
from .models.execution import ExecutionCursor

__version__ = '0.2.0'
__all__ = [
    'Problem', 'Query', 'Answer', 'AnsweredQuery', 'AlgorithmPolicy',
    'SingleCandidateStop', 'VolumeConfidenceStop', 'QueryBudget',
    'SolverExecution', 'SolverEvent', 'SolveResult', 'solve', 'ExecutionCursor',
    'SolveContinuation', 'continuation_from_result',
]
