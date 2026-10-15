"""Real public SDK callbacks exercise optional display and parent diagnostics."""
import io
import os
import pstats
import time
from uuid import uuid4

import pytest

import otqa
from otqa.answers import SimulatedAnswers
from otqa.errors import ObserverError, RecorderError
from otqa.runtime.case import error_wire
from otqa.runtime.codec import encode, read_json
from otqa.runtime.documents import resolve_ref
from otqa.runtime.profiling import ParentCallProfiler
from otqa.runtime.project import load_project_context
from otqa.runtime.storage import PersistenceError, create_directory
from otqa.runtime.telemetry import TelemetryObserver, terminal_display


def attempt_at(tmp_path):
    (tmp_path / 'otqa-project.json').write_bytes(encode({'schema_version': 1, 'project_kind': 'otqa_project', 'project_id': str(uuid4())}))
    context = load_project_context(tmp_path)
    attempt = tmp_path / 'runs' / 'attempt'
    create_directory(context, attempt)
    return context, attempt


def solve(observer=None, recorder=None):
    policy = otqa.AlgorithmPolicy('fixed', 1, 'both', 5, 'candidate_count', otqa.SingleCandidateStop())
    calls = []
    def provider(query):
        calls.append(query)
        return SimulatedAnswers((.7, .3))(query)
    result = otqa.solve(otqa.Problem(((1., 0.), (0., 1.))), policy, provider,
                        execution=otqa.SolverExecution(1), budget=otqa.QueryBudget(4), observer=observer, recorder=recorder)
    return result, calls


def broken_display(event):
    raise BrokenPipeError('constructed broken terminal')


def test_continue_display_failure_is_durable_and_does_not_repeat_answer(tmp_path):
    context, attempt = attempt_at(tmp_path)
    observer = TelemetryObserver(context, attempt, 'continue', broken_display)
    baseline, baseline_calls = solve()
    result, calls = solve(observer)
    assert result == baseline
    # Equivalent ratio choices can require different valid trajectory lengths
    # across numerical builds. The observer must preserve the actual trajectory.
    assert calls == baseline_calls == [record.query for record in result.queries]
    assert calls
    assert result.query_counts.dispatched_new == result.query_counts.answered_new == len(calls)
    diagnostic = read_json(attempt / 'telemetry/error000001.json')
    assert observer.errors == [diagnostic]
    assert diagnostic['code'] == 'observer'
    assert diagnostic['context']['failure_policy'] == 'continue'
    assert diagnostic['context']['event_type'] == 'StateAnalyzed'
    assert observer.sink is None and observer.elapsed >= 0


def test_abort_display_failure_propagates_observer_error_and_persists_diagnostic(tmp_path):
    context, attempt = attempt_at(tmp_path)
    observer = TelemetryObserver(context, attempt, 'abort', broken_display)
    with pytest.raises(ObserverError) as raised:
        solve(observer)
    assert raised.value.context.query_counts.dispatched_new == 0
    assert raised.value.context.query_counts.answered_new == 0
    assert error_wire(raised.value)['code'] == 'observer'
    assert read_json(attempt / 'telemetry/error000001.json') == observer.errors[0]


def test_continue_cannot_swallow_required_diagnostic_publication_failure(tmp_path, monkeypatch):
    context, attempt = attempt_at(tmp_path)
    def fail(*args, **kwargs):
        raise PersistenceError('constructed diagnostic fsync failure')
    monkeypatch.setattr('otqa.runtime.telemetry.publish_json', fail)
    observer = TelemetryObserver(context, attempt, 'continue', broken_display)
    with pytest.raises(ObserverError) as raised:
        solve(observer)
    assert raised.value.context.query_counts.dispatched_new == 0
    assert error_wire(raised.value)['code'] == 'persistence_failure'
    assert observer.errors == []


def test_required_recorder_failure_never_reaches_optional_display(tmp_path):
    context, attempt = attempt_at(tmp_path)
    seen = []
    observer = TelemetryObserver(context, attempt, 'continue', seen.append)
    def failed_recorder(event):
        raise OSError('required recorder failed')
    with pytest.raises(RecorderError):
        solve(observer, failed_recorder)
    assert seen == [] and observer.errors == []


def test_redirected_output_has_no_optional_display():
    assert terminal_display(io.StringIO()) is None


def test_cprofile_contains_actual_public_solver_and_bound_raw_reports(tmp_path):
    context, attempt = attempt_at(tmp_path)
    (attempt / 'manifest.json').write_bytes(b'{}\n')
    profiler = ParentCallProfiler()
    started = time.perf_counter()
    profiler.start()
    try:
        result, calls = solve()
    finally:
        profiler.stop()
    assert result.exactly_solved
    assert calls == [record.query for record in result.queries]
    assert calls
    assert result.query_counts.dispatched_new == result.query_counts.answered_new == len(calls)
    profiler.publish(context, attempt, attempt, str(uuid4()), 'attempt0001', [{'metric_id': 'api_call', 'scope': 'wall', 'aggregation': 'inclusive', 'value': time.perf_counter() - started, 'unit': 'seconds'}])
    document = read_json(attempt / 'profile.json')
    assert document['collector'] == 'cprofile'
    raw = [resolve_ref(attempt, ref) for ref in document['raw_reports']]
    assert len(raw) == 2
    stats = pstats.Stats(str(raw[0]))
    assert any(filename.endswith('/otqa/solver.py') and name == 'publish' for (filename, _, name) in stats.stats)
    text = raw[1].read_text()
    assert f'process_pid={os.getpid()}' in text
    assert 'Workers are not instrumented' in text
