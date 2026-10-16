"""The single synchronous solver loop and its owned session lifecycle."""
from __future__ import annotations

from collections.abc import Callable, Sequence

from .config import AlgorithmPolicy, QueryBudget, SolverExecution, VolumeConfidenceStop
from .continuation import SolveContinuation, continuation_binding
from .execution import initial_cursor, requires_full_retry, resolve_cycle, validate_attempt, validate_cursor
from .errors import (
    AnswerProviderError, ExecutionContextError, InfeasibleStateError, InputValidationError,
    NumericalError, ObserverError, PlanningInvariantError, RecorderError, SolverError,
)
from .models import (
    Answer, AnsweredQuery, AnswerReceived, PartialContext, Problem, Query, QueryCompleted,
    QueryCounts, QueryDispatched, QueryPlanned, QueryRecord, SolveFinished, SolveResult,
    SolverEvent, StateAnalyzed,
    PlanningAttemptStarted, PlanningAttemptCompleted, PlanningResolved,
)
from .models.core import validate_answer
from .models.execution import PendingPlanningCycle


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
                       recorder, observer, continuation=None) -> SolveResult:
    if not isinstance(problem, Problem) or not isinstance(policy, AlgorithmPolicy):
        raise InputValidationError('solve requires Problem and AlgorithmPolicy instances')
    if not isinstance(budget, QueryBudget) or not isinstance(execution, SolverExecution):
        raise InputValidationError('solve requires QueryBudget and SolverExecution instances')
    if not callable(answer_provider) or any(callback is not None and not callable(callback)
                                            for callback in (recorder, observer)):
        raise InputValidationError('provider, recorder and observer must be callable')
    history = _validated_history(problem, initial_answers)
    if continuation is not None:
        if not isinstance(continuation, SolveContinuation):
            raise InputValidationError('continuation must be a SolveContinuation')
        if history:
            raise InputValidationError('continuation and nonempty initial_answers are mutually exclusive')
        continuation.validate_for(problem, policy)
        history, cursor = continuation.answers, continuation.execution_cursor
    else:
        cursor = initial_cursor(policy, len(history))
    from .planning import PlannerSession
    session = PlannerSession(problem, policy, execution)
    return _drive(problem, policy, answer_provider, budget=budget, history=history,
                  recorder=recorder, observer=observer, session=session, execution_cursor=cursor)


def _drive(problem: Problem, policy: AlgorithmPolicy, answer_provider: Callable[[Query], Answer], *,
           budget: QueryBudget, history: tuple[AnsweredQuery, ...], recorder, observer,
           session, execution_cursor=None) -> SolveResult:
    """Internal injection seam shares exactly the public loop and cleanup path."""
    answers = list(history)
    records: list[QueryRecord] = []
    cycles = []
    cursor = execution_cursor if execution_cursor is not None else initial_cursor(policy, len(history))
    pending_cycle = None
    binding = continuation_binding(problem, policy)
    initial_count = len(history)
    dispatched = 0
    last_state = None
    open_query = None
    close_attempted = False

    def counts() -> QueryCounts:
        return QueryCounts(initial_count, dispatched, len(answers) - initial_count, len(answers))

    def context() -> PartialContext:
        return PartialContext(last_state, tuple(answers), tuple(records), counts(), open_query,
                              cursor, tuple(cycles), pending_cycle, binding)

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
        validate_cursor(policy, cursor, len(history))
        state = compute(session.initial_state, history)
        pending = None
        while True:
            analysis = compute(session.analyze, state, volumes=True)
            if not analysis.feasible:
                raise InfeasibleStateError('query trajectory became infeasible', context=context())
            last_state = analysis
            if analysis.answered_total != len(answers):
                raise PlanningInvariantError('actual analysis differs from accepted answer history', context=context())
            publish(StateAnalyzed(analysis, cursor))
            if not analysis.candidate_indices:
                raise PlanningInvariantError('feasible query state has no candidate alternatives', context=context())
            if pending is not None:
                decision, previous, answered, cycle = pending
                record = QueryRecord(answered.query, answered.answer, decision, previous, analysis, cycle)
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
            attempts = []

            def attempt_at(requested_depth):
                nonlocal pending_cycle
                index = len(attempts) + 1
                pending_cycle = PendingPlanningCycle(cursor, tuple(attempts), index, requested_depth)
                publish(PlanningAttemptStarted(cursor, analysis, index, requested_depth))
                attempted = compute(session.plan, state, requested_depth=requested_depth)
                validate_attempt(policy, attempted, requested_depth, analysis.candidate_count)
                attempts.append(attempted)
                pending_cycle = PendingPlanningCycle(cursor, tuple(attempts))
                publish(PlanningAttemptCompleted(cursor, analysis, index, attempted))
                return attempted

            attempted = attempt_at(cursor.remaining_depth)
            if requires_full_retry(policy, cursor, attempted):
                attempt_at(policy.depth)
            cycle = resolve_cycle(policy, cursor, tuple(attempts))
            cycles.append(cycle)
            pending_cycle = None
            publish(PlanningResolved(cycle, analysis))
            decision = cycle.selected_plan
            if decision is None:
                reason = cycle.outcome
                break
            decision.query.validate_for(problem)
            publish(QueryPlanned(decision, analysis, cycle))
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
            cursor = cycle.proposed_cursor_after_answer
            publish(AnswerReceived(accepted, counts(), cursor))
            pending = decision, analysis, accepted, cycle
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
            execution_cursor=cursor, planning_cycles=tuple(cycles),
            continuation_binding=binding,
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
