"""Optimal Tradeoff Queries: mathematical SDK with an independent runtime."""
from .api import solve
from .config import AlgorithmPolicy, QueryBudget, SingleCandidateStop, SolverExecution, VolumeConfidenceStop
from .models import Answer, AnsweredQuery, Problem, Query, SolveResult, SolverEvent

__version__ = '0.1.0'
__all__ = [
    'Problem', 'Query', 'Answer', 'AnsweredQuery', 'AlgorithmPolicy',
    'SingleCandidateStop', 'VolumeConfidenceStop', 'QueryBudget',
    'SolverExecution', 'SolverEvent', 'SolveResult', 'solve',
]
