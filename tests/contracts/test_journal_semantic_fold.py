"""Differential readers and declarative prefixes; no solver or external archive."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from otqa.runtime import journal, journal_v1
from otqa.runtime.codec import DocumentError, digest, encode, mathematical_hex
from test_countdown_policy import configuration, journal_events


def reference(name):
    path = Path(__file__).with_name('fixtures') / (name + '_before_semantic_fold.py')
    spec = spec_from_file_location('otqa.runtime._test_reference_' + name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OLD_V1 = reference('journal_v1')
OLD_V2 = reference('journal_v2')
OLD_V2.legacy = OLD_V1


def packed(events):
    return b''.join(encode(event) for event in events)


def outcome(reader, data, count, **kwargs):
    try:
        return 'accepted', reader(data, len(data), digest(data), count, **kwargs)
    except DocumentError as error:
        return 'rejected', str(error)


def reseal(events):
    for index, event in enumerate(events, 1):
        event['sequence'] = index
        event['monotonic_ns'] = index
        event['numeric_hex'] = mathematical_hex(event['payload'], '/payload')
    return events


def progress(plan, threshold):
    terminal = plan['selected']['score']['expected_terminal_candidates']
    return {'basis': 'candidate_count', 'starting_value': 2.,
        'expected_terminal_value': terminal, 'expected_progress': 2. - terminal,
        'threshold': threshold, 'comparison': 'strict_greater',
        'admissible': threshold is None or 2. - terminal > threshold}


def attempt(depth, plan=None, threshold=.001):
    evidence = progress(plan, threshold) if plan is not None else None
    result = 'available' if plan is not None else 'no_query'
    horizon = {'horizon': depth, 'generated_query_count': int(plan is not None),
        'evaluated_query_count': int(plan is not None), 'outcome': result,
        'selected_plan': plan, 'selected_progress': evidence,
        'best_progress_witness': plan, 'best_progress': evidence}
    return {'requested_depth': depth, 'evaluated_horizons': [depth], 'outcome': result,
        'selected_plan': plan, 'selected_progress': evidence,
        'best_progress_witness': plan, 'horizon_evidence': [horizon]}


def v2_events(depth, *, shortened=False, full=False, threshold=.001):
    """Explicit one-block state/answer chain plus a terminal empty inventory."""
    source = journal_events(0, list(range(depth, 0, -1)))
    cursor = {'answered_total': 0, 'remaining_depth': 1 if shortened else depth}
    initial_cursor = dict(cursor)
    result = []
    cycle = None

    def append(kind, payload, query_id=None):
        result.append({**source[0], 'schema_version': 2,
            'event_type': kind, 'query_id': query_id, 'payload': deepcopy(payload)})

    def resolve(plan):
        nonlocal cycle
        requested = cursor['remaining_depth']
        attempts = []
        if requested < depth:
            attempts.append(attempt(requested, threshold=threshold))
        attempts.append(attempt(depth if plan is None else plan['selected']['horizon'], plan, threshold))
        # A normal countdown phase that has a query needs no replacement.
        if plan is not None and plan['selected']['horizon'] == requested:
            attempts = [attempt(requested, plan, threshold)]
        for index, item in enumerate(attempts, 1):
            append('planning_attempt_started', {'state_before_index': cursor['answered_total'],
                'execution_cursor': cursor, 'attempt_index': index,
                'requested_depth': item['requested_depth']})
            append('planning_attempt_completed', {'state_before_index': cursor['answered_total'],
                'execution_cursor': cursor, 'attempt_index': index, 'attempt': item})
        proposed = None if plan is None else {'answered_total': cursor['answered_total'] + 1,
            'remaining_depth': plan['selected']['horizon'] - 1 if plan['selected']['horizon'] > 1 else depth}
        cycle = {'cursor_before': dict(cursor), 'attempts': attempts, 'selected_plan': plan,
            'outcome': attempts[-1]['outcome'], 'restart_reason': 'no_query' if len(attempts) == 2 else None,
            'proposed_cursor_after_answer': proposed}
        append('planning_resolved', {'state_before_index': cursor['answered_total'], 'cycle': cycle})

    for old in source:
        kind, payload = old['event_type'], deepcopy(old['payload'])
        if kind == 'query_planned':
            if full:
                plan = payload['planning']
                plan['plan_tree'] = {'node_id': 'root', 'candidate_count': 2,
                    'stop_reason': None, 'maximum_volume_share': None,
                    'query': plan['selected']['query'], 'expected_terminal_candidates': 1.5,
                    'expected_terminal_loss': 1.5, 'branches': []}
            resolve(payload['planning'])
        elif kind == 'answer_received':
            cursor = deepcopy(cycle['proposed_cursor_after_answer'])
        elif kind == 'query_completed':
            payload['planning_cycle'] = deepcopy(cycle)
            # The full tree is an existing retained payload, not recomputed.
            payload['planning'] = deepcopy(cycle['selected_plan'])
        elif kind == 'run_finished':
            resolve(None)
        if kind in ('run_started', 'state_analyzed', 'answer_received', 'run_finished'):
            payload['execution_cursor'] = deepcopy(cursor)
        append(kind, payload, old['query_id'])
    algorithm = {**configuration()['algorithm'], 'depth': depth,
        'horizon_execution': 'countdown', 'min_expected_progress': threshold}
    return reseal(result), {'algorithm': algorithm, 'budget': {'max_queries': None},
        'alternative_ids': ['a', 'b'], 'initial_execution_cursor': initial_cursor}


@pytest.mark.parametrize('depth', [1, 2, 3])
def test_v1_every_prefix_matches_frozen_reader_with_unchanged_inputs(depth):
    events = journal_events(2, list(range(depth, 0, -1)))
    original = deepcopy(events)
    for end in range(1, len(events) + 1):
        data = packed(events[:end])
        assert outcome(journal_v1.verify_prefix, data, end, initial_answers=2) == outcome(
            OLD_V1.verify_prefix, data, end, initial_answers=2)
    assert events == original


@pytest.mark.parametrize('depth,shortened', [(1, False), (2, False), (2, True), (3, False), (3, True)])
@pytest.mark.parametrize('full', [False, True])
@pytest.mark.parametrize('threshold', [None, .001])
def test_v2_every_durable_and_partial_prefix_matches_frozen_transcode(depth, shortened, full, threshold):
    events, kwargs = v2_events(depth, shortened=shortened, full=full, threshold=threshold)
    original = deepcopy(events)
    for end in range(1, len(events) + 1):
        data = packed(events[:end])
        actual = outcome(journal.verify_prefix, data, end, **kwargs)
        assert actual[0] == 'accepted', actual
        assert actual == outcome(OLD_V2.verify_prefix, data, end, **kwargs)
    assert events == original


def mutate(events, name):
    target = next(e for e in events if e['event_type'] == 'answer_received')
    if name == 'state-index':
        next(e for e in events if e['event_type'] == 'state_analyzed')['payload']['state_index'] = 99
    elif name == 'dispatch-query':
        next(e for e in events if e['event_type'] == 'query_dispatched')['payload']['query']['value'] = .75
    elif name == 'answer-counter':
        target['payload']['answered_new'] = 99
    elif name == 'signed-zero':
        target['payload']['query']['value'] = -0.
    elif name == 'duplicate-completion':
        completed = next(e for e in events if e['event_type'] == 'query_completed')
        events.insert(events.index(completed), deepcopy(completed))
    elif name == 'wrong-terminal':
        events[-1]['payload']['termination_reason'] = 'exact_single_candidate'
    elif name == 'missing-dispatch':
        events.remove(next(e for e in events if e['event_type'] == 'query_dispatched'))
    elif name == 'identity':
        target['run_id'] = '22222222-2222-2222-2222-222222222222'
    elif name == 'answer-type':
        target['payload']['answer'] = 'invalid'
    elif name == 'plan-binding':
        next(e for e in events if e['event_type'] == 'query_completed')['payload']['planning']['selected']['query']['value'] = 1.25
    else:
        raise AssertionError(name)
    return reseal(events)


@pytest.mark.parametrize('version', [1, 2])
@pytest.mark.parametrize('name', ['state-index', 'dispatch-query', 'answer-counter', 'signed-zero',
    'duplicate-completion', 'wrong-terminal', 'missing-dispatch', 'identity', 'answer-type', 'plan-binding'])
def test_rehashed_semantic_and_schema_corruption_matches_frozen_rejection(version, name):
    events, kwargs = (journal_events(0, [2, 1]), {}) if version == 1 else v2_events(2, shortened=True)
    events = mutate(events, name)
    data = packed(events)
    current, before = (journal_v1, OLD_V1) if version == 1 else (journal, OLD_V2)
    actual = outcome(current.verify_prefix, data, len(events), **kwargs)
    assert actual[0] == 'rejected'
    assert actual == outcome(before.verify_prefix, data, len(events), **kwargs)


@pytest.mark.parametrize('version', [1, 2])
@pytest.mark.parametrize('name', ['sequence', 'monotonic', 'hex', 'truncated', 'digest', 'count'])
def test_original_byte_and_numeric_guards_are_not_bypassed(version, name):
    events, kwargs = (journal_events(0, [2]), {}) if version == 1 else v2_events(2)
    if name == 'sequence':
        events[1]['sequence'] = 10
    elif name == 'monotonic':
        events[1]['monotonic_ns'] = 0
    elif name == 'hex':
        next(event for event in events if event['numeric_hex'])['numeric_hex'] = {}
    data = packed(events)
    if name == 'truncated':
        data = data[:-1]
    arguments = (data, len(data), 'f' * 64 if name == 'digest' else digest(data),
        len(events) + int(name == 'count'))
    current, before = (journal_v1, OLD_V1) if version == 1 else (journal, OLD_V2)
    with pytest.raises(DocumentError) as actual:
        current.verify_prefix(*arguments, **kwargs)
    with pytest.raises(DocumentError) as old:
        before.verify_prefix(*arguments, **kwargs)
    assert str(actual.value) == str(old.value)


def test_v1_does_not_read_later_invalid_json_before_current_semantic_error():
    events = journal_events(0, [2])
    events[1]['payload']['state_index'] = 99
    reseal(events)
    data = packed(events[:2]) + b'{bad-json}\n'
    actual = outcome(journal_v1.verify_prefix, data, 3)
    assert actual == outcome(OLD_V1.verify_prefix, data, 3)
    assert actual == ('rejected', 'State index differs from accepted answer count')


@pytest.mark.parametrize('version', [1, 2])
@pytest.mark.parametrize('numeric', [-0., 0., 0, 1])
def test_retained_numeric_types_and_signed_zero_match_reference(version, numeric):
    events, kwargs = (journal_events(0, [2, 1]), {}) if version == 1 else v2_events(2, full=True)
    def change_queries(value):
        if isinstance(value, dict):
            if {'goal_index_a', 'goal_index_b', 'value'} <= set(value):
                value['value'] = numeric
            for child in value.values():
                change_queries(child)
        elif isinstance(value, list):
            for child in value:
                change_queries(child)
    change_queries(events)
    data = packed(reseal(events))
    current, before = (journal_v1, OLD_V1) if version == 1 else (journal, OLD_V2)
    actual = outcome(current.verify_prefix, data, len(events), **kwargs)
    assert actual[0] == 'accepted'
    assert actual == outcome(before.verify_prefix, data, len(events), **kwargs)


def test_v2_never_calls_frozen_byte_reader_or_reencodes_a_synthetic_journal(monkeypatch):
    events, kwargs = v2_events(3, shortened=True, full=True)
    data = packed(events)
    expected = OLD_V2.verify_prefix(data, len(data), digest(data), len(events), **kwargs)
    def forbidden(*args, **kw):
        raise AssertionError('v2 must fold its already validated records directly')
    monkeypatch.setattr(journal_v1, 'verify_prefix', forbidden)
    assert journal.verify_prefix(data, len(data), digest(data), len(events), **kwargs) == expected


def test_v2_schema_admission_runs_once_for_each_original_record(monkeypatch):
    events, kwargs = v2_events(3, shortened=True, full=True)
    data = packed(events)
    validate = journal.validate
    admitted = []
    def checked(kind, event):
        admitted.append((kind, event['schema_version'], event['sequence']))
        return validate(kind, event)
    def forbidden(*args, **kw):
        raise AssertionError('no synthetic legacy schema admission')
    monkeypatch.setattr(journal, 'validate', checked)
    monkeypatch.setattr(journal_v1, 'validate', forbidden)
    journal.verify_prefix(data, len(data), digest(data), len(events), **kwargs)
    assert admitted == [('event', 2, index) for index in range(1, len(events) + 1)]


@pytest.mark.parametrize('corruption', ['cursor', 'gain', 'missing-resolution', 'missing-fallback-start'])
def test_original_v2_phase_and_progress_checks_still_reject(corruption):
    events, kwargs = v2_events(3, shortened=True, full=True)
    if corruption == 'cursor':
        next(e for e in events if e['event_type'] == 'answer_received')['payload']['execution_cursor']['remaining_depth'] = 3
    elif corruption == 'gain':
        completed = next(e for e in events if e['event_type'] == 'planning_attempt_completed'
                         and e['payload']['attempt']['outcome'] == 'available')
        completed['payload']['attempt']['selected_progress']['expected_progress'] += .25
    elif corruption == 'missing-resolution':
        events.remove(next(e for e in events if e['event_type'] == 'planning_resolved'))
    else:
        events.remove(next(e for e in events if e['event_type'] == 'planning_attempt_started'
                           and e['payload']['attempt_index'] == 2))
    data = packed(reseal(events))
    actual = outcome(journal.verify_prefix, data, len(events), **kwargs)
    assert actual[0] == 'rejected'
    assert actual == outcome(OLD_V2.verify_prefix, data, len(events), **kwargs)
