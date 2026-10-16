"""Terminal planning proofs and explicit compatibility boundaries."""
from copy import deepcopy
import pytest
from otqa.runtime.codec import DocumentError, decode, digest, encode, mathematical_hex
from otqa.runtime.documents import convert_config_document
from otqa.runtime.journal import verify_prefix
from otqa.runtime.schema import validate
from otqa.runtime.validation import journal_policy, verify_result
from test_runtime_policy_readers import recorded_result
from test_countdown_policy import configuration


def test_converter_preserves_disabled_historical_threshold_and_original_bytes():
    old = configuration()
    before = encode(old)
    new = convert_config_document(old)
    assert encode(old) == before
    assert new['schema_version'] == 2
    assert new['algorithm']['min_expected_progress'] is None
    assert new['algorithm']['horizon_execution'] == 'receding'
    assert convert_config_document(old, min_expected_progress=.001)['algorithm']['min_expected_progress'] == .001
    old['algorithm']['horizon_execution'] = 'countdown'
    with pytest.raises(DocumentError, match='explicit acceptance'):
        convert_config_document(old)
    assert convert_config_document(old, countdown_semantics_confirmed=True)['algorithm']['horizon_execution'] == 'countdown'


@pytest.mark.parametrize('bad', [True, '0.001', -1, float('inf'), float('nan')])
def test_v2_threshold_is_typed_and_finite(bad):
    new = convert_config_document(configuration())
    new['algorithm']['min_expected_progress'] = bad
    with pytest.raises(DocumentError):
        validate('config', new)


def test_new_native_config_requires_explicit_threshold():
    new = convert_config_document(configuration())
    del new['algorithm']['min_expected_progress']
    with pytest.raises(DocumentError):
        validate('config', new)


def checked_events(root, manifest, events):
    adjusted = []
    for index, event in enumerate(events, 1):
        event = deepcopy(event)
        event['sequence'] = index
        event['numeric_hex'] = mathematical_hex(event['payload'], '/payload')
        adjusted.append(event)
    data = b''.join(encode(e) for e in adjusted)
    return verify_prefix(data, len(data), digest(data), len(adjusted),
        **journal_policy(manifest, root, root / 'manifest.json'))


@pytest.mark.parametrize('execution', ['receding', 'countdown'])
def test_insufficient_progress_is_committed_unsolved_without_dispatch(tmp_path, execution):
    _, root, manifest, payload, result = recorded_result(tmp_path, depth=2,
        horizon_execution=execution, min_progress=10.)
    assert result['execution_status'] == 'completed'
    solver = result['solver_result']
    assert solver['termination_reason'] == 'insufficient_expected_progress'
    assert not solver['solved'] and solver['selected_candidate_id'] is None
    assert result['query_counts']['dispatched_new'] == result['query_counts']['answered_new'] == 0
    assert verify_result(root / 'result.json', root, payload) == result
    events = [decode(line) for line in (root / 'events.jsonl').read_bytes().splitlines()]
    prefix = checked_events(root, manifest, events)
    assert prefix['planning_attempts_started'] == prefix['planning_attempts_completed'] == 1
    assert prefix['planning_cycles'][-1]['outcome'] == 'insufficient_expected_progress'


@pytest.mark.parametrize('kind', ['planning_resolved', 'planning_attempt_completed', 'planning_attempt_started'])
def test_rehashed_missing_terminal_evidence_is_rejected(tmp_path, kind):
    _, root, manifest, _, _ = recorded_result(tmp_path, depth=2, min_progress=10.)
    events = [decode(line) for line in (root / 'events.jsonl').read_bytes().splitlines()]
    with pytest.raises(DocumentError):
        checked_events(root, manifest, [e for e in events if e['event_type'] != kind])


def test_rehashed_witness_gain_tampering_is_rejected(tmp_path):
    _, root, manifest, _, _ = recorded_result(tmp_path, depth=2, min_progress=10.)
    events = [decode(line) for line in (root / 'events.jsonl').read_bytes().splitlines()]
    completed = next(e for e in events if e['event_type'] == 'planning_attempt_completed')
    completed['payload']['attempt']['horizon_evidence'][0]['best_progress']['expected_progress'] += .1
    with pytest.raises(DocumentError, match='progress|subtraction'):
        checked_events(root, manifest, events)


def test_accepted_answer_phase_cannot_be_reset_with_valid_hashes(tmp_path):
    _, root, manifest, _, _ = recorded_result(tmp_path, depth=2, horizon_execution='countdown')
    events = [decode(line) for line in (root / 'events.jsonl').read_bytes().splitlines()]
    answered = next(e for e in events if e['event_type'] == 'answer_received')
    answered['payload']['execution_cursor']['remaining_depth'] = 2
    with pytest.raises(DocumentError, match='execution phase'):
        checked_events(root, manifest, events)


def test_starting_phase_changes_v2_mathematical_identity_but_paths_do_not():
    from otqa.runtime.serialization import mathematical_input_digest
    config = convert_config_document(configuration(), countdown_semantics_confirmed=True)
    problem = {'alternatives': [[1., 0.], [0., 1.]]}
    answers = [{'goal_index_a': 0, 'goal_index_b': 1, 'value': .3, 'answer': '>'}]
    first = {'answers': answers, 'execution_cursor': {'answered_total': 1, 'remaining_depth': 1}}
    second = {'answers': answers, 'execution_cursor': {'answered_total': 1, 'remaining_depth': 2}}
    a = mathematical_input_digest(problem, config, 'simulated', None, None, None, continuation=first)
    b = mathematical_input_digest(problem, config, 'simulated', None, None, None, continuation=second)
    assert a != b
    first['unused_path'] = 'different/location'
    assert mathematical_input_digest(problem, config, 'simulated', None, None, None, continuation=first) == a


def test_no_query_has_explicit_committed_empty_inventory_evidence(tmp_path):
    _, root, manifest, payload, result = recorded_result(tmp_path, matrix=((1., 0.), (1., 0.)), depth=1)
    assert result['solver_result']['termination_reason'] == 'no_query'
    assert verify_result(root / 'result.json', root, payload) == result
    events = [decode(line) for line in (root / 'events.jsonl').read_bytes().splitlines()]
    checked = checked_events(root, manifest, events)
    attempt = checked['planning_cycles'][-1]['attempts'][-1]
    assert attempt['outcome'] == 'no_query'
    assert attempt['horizon_evidence'][0]['evaluated_query_count'] == 0
    assert result['query_counts']['dispatched_new'] == 0


@pytest.mark.parametrize('depth', [2, 3])
def test_stop_aware_confidence_countdown_roundtrips_full_durable_evidence(tmp_path, depth):
    _, root, _, payload, result = recorded_result(tmp_path, threshold=.95, planning='stop_aware',
        depth=depth, horizon_execution='countdown', min_progress=.001)
    assert result['solver_result']['solved']
    assert verify_result(root / 'result.json', root, payload) == result
    for cycle in result['solver_result']['planning_cycles']:
        for attempt in cycle['attempts']:
            assert attempt['selected_progress']['basis'] == 'effective_loss'
