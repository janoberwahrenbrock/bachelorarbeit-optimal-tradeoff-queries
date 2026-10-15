"""The single synchronous solver loop and its owned session lifecycle."""
from __future__ import annotations

from collections.abc import Callable, Sequence

from .config import AlgorithmPolicy, QueryBudget, SolverExecution, VolumeConfidenceStop
from .errors import (
    AnswerProviderError, ExecutionContextError, InfeasibleStateError, InputValidationError,
    NumericalError, ObserverError, PlanningInvariantError, RecorderError, SolverError,
)
from .models import (
    Answer, AnsweredQuery, AnswerReceived, PartialContext, Problem, Query, QueryCompleted,
    QueryCounts, QueryDispatched, QueryPlanned, QueryRecord, SolveFinished, SolveResult,
    SolverEvent, StateAnalyzed,
)
from .models.core import validate_answer
from .models.planning import NoQuery


def _validated_history(problem: Problem, answers: Sequence[AnsweredQuery]) -> tuple[AnsweredQuery, ...]:
    try:
        history = tuple(answers)
    except TypeError as exc:
        raise InputValidationError('initial_answers must be a sequence of AnsweredQuery') from exc
    for answer in history:
        if not isinstance(answer, AnsweredQuery):
            raise InputValidationError('initial_answers must contain only AnsweredQuery')
        answer.query.validate_for(problem)
    return history


def solve_with_session(problem, policy, answer_provider, *, budget, execution, initial_answers,
                       recorder, observer) -> SolveResult:
    if not isinstance(problem, Problem) or not isinstance(policy, AlgorithmPolicy):
        raise InputValidationError('solve requires Problem and AlgorithmPolicy instances')
    if not isinstance(budget, QueryBudget) or not isinstance(execution, SolverExecution):
        raise InputValidationError('solve requires QueryBudget and SolverExecution instances')
    if not callable(answer_provider) or any(callback is not None and not callable(callback)
                                            for callback in (recorder, observer)):
        raise InputValidationError('provider, recorder and observer must be callable')
    history = _validated_history(problem, initial_answers)
    from .planning import PlannerSession
    session = PlannerSession(problem, policy, execution)
    return _drive(problem, policy, answer_provider, budget=budget, history=history,
                  recorder=recorder, observer=observer, session=session)


def _drive(problem: Problem, policy: AlgorithmPolicy, answer_provider: Callable[[Query], Answer], *,
           budget: QueryBudget, history: tuple[AnsweredQuery, ...], recorder, observer,
           session) -> SolveResult:
    """Internal injection seam shares exactly the public loop and cleanup path."""
    answers = list(history)
    records: list[QueryRecord] = []
    initial_count = len(history)
    dispatched = 0
    last_state = None
    open_query = None
    close_attempted = False

    def counts() -> QueryCounts:
        return QueryCounts(initial_count, dispatched, len(answers) - initial_count, len(answers))

    def context() -> PartialContext:
        return PartialContext(last_state, tuple(answers), tuple(records), counts(), open_query)

    def publish(event: SolverEvent) -> None:
        for callback, category in ((recorder, RecorderError), (observer, ObserverError)):
            if callback is not None:
                try:
                    callback(event)
                except Exception as exc:
                    raise category(str(exc), context=context()) from exc

    def compute(operation, *args, **kwargs):
        try:
            return operation(*args, **kwargs)
        except SolverError:
            raise
        except Exception as exc:
            raise NumericalError(str(exc), context=context()) from exc

    try:
        state = compute(session.initial_state, history)
        pending = None
        while True:
            analysis = compute(session.analyze, state, volumes=True)
            if not analysis.feasible:
                raise InfeasibleStateError('query trajectory became infeasible', context=context())
            last_state = analysis
            publish(StateAnalyzed(analysis))
            if not analysis.candidate_indices:
                raise PlanningInvariantError('feasible query state has no candidate alternatives', context=context())
            if pending is not None:
                decision, previous, answered = pending
                record = QueryRecord(answered.query, answered.answer, decision, previous, analysis)
                records.append(record)
                publish(QueryCompleted(record))
                pending = None
                open_query = None

            selected = None
            shares = dict(analysis.candidate_volume_shares)
            volumes = dict(analysis.candidate_volumes)
            if analysis.candidate_count == 1:
                reason = 'exact_single_candidate'
                selected = analysis.candidate_indices[0]
            elif isinstance(policy.stopping, VolumeConfidenceStop) and shares:
                if any(index not in shares for index in analysis.candidate_indices):
                    raise PlanningInvariantError('confidence shares do not cover candidates', context=context())
                maximum = min(analysis.candidate_indices, key=lambda index: (-shares[index], index))
                if shares[maximum] >= policy.stopping.threshold:
                    reason, selected = 'volume_confidence', maximum
            if selected is not None:
                break
            if budget.max_queries is not None and len(answers) >= budget.max_queries:
                reason = 'max_questions'
                break
            decision = compute(session.plan, state)
            if isinstance(decision, NoQuery):
                reason = 'no_query'
                break
            decision.query.validate_for(problem)
            publish(QueryPlanned(decision, analysis))
            dispatched += 1
            open_query = decision.query
            publish(QueryDispatched(decision.query, counts()))
            try:
                answer = answer_provider(decision.query)
            except Exception as exc:
                raise AnswerProviderError(str(exc), context=context()) from exc
            validate_answer(answer)
            accepted = AnsweredQuery(decision.query, answer)
            answers.append(accepted)
            publish(AnswerReceived(accepted, counts()))
            pending = decision, analysis, accepted
            state = compute(session.advance, state, accepted)

        result = SolveResult(
            solved=selected is not None,
            exactly_solved=reason == 'exact_single_candidate',
            termination_reason=reason,
            selected_candidate_index=selected,
            selected_candidate_volume=volumes.get(selected) if selected is not None else None,
            selected_candidate_volume_share=shares.get(selected) if selected is not None else None,
            final_state=analysis,
            answers=tuple(answers), queries=tuple(records), query_counts=counts(),
        )
        close_attempted = True
        try:
            session.close()
        except Exception as exc:
            raise ExecutionContextError('session cleanup failed', context=context()) from exc
        publish(SolveFinished(result))
        return result
    except BaseException as primary:
        if isinstance(primary, SolverError) and primary.context is None:
            primary.context = context()
        if not close_attempted:
            try:
                session.close()
            except BaseException as cleanup:
                primary.add_note(f'Additional session cleanup failure: {type(cleanup).__name__}: {cleanup}')
                if isinstance(primary, SolverError):
                    primary.cleanup_errors = (cleanup,)
        raise
