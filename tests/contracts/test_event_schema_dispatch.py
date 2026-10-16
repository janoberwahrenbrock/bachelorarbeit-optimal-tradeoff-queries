"""Discriminated validation keeps full-schema admission and error evidence."""
from copy import deepcopy
import math

import pytest

from otqa.runtime import schema
from otqa.runtime.codec import DocumentError, read_json
from test_runtime_policy_readers import recorded_result


@pytest.fixture(scope='module')
def event_samples(tmp_path_factory):
    _, root, _, _, _ = recorded_result(tmp_path_factory.mktemp('event-dispatch'), depth=2)
    import json
    events = [json.loads(line) for line in (root / 'events.jsonl').read_bytes().splitlines()]
    by_type = {event['event_type']: event for event in events}
    terminal = by_type['run_finished']
    by_type['run_failed'] = {**terminal, 'event_type': 'run_failed', 'payload': {
        'error': {'code': 'worker_failure', 'type': 'ExampleError', 'message': 'constructed',
                  'traceback': None, 'stage': 'worker', 'context': {}},
        'query_counts': terminal['payload']['query_counts']}}
    by_type['run_interrupted'] = {**terminal, 'event_type': 'run_interrupted', 'payload': {
        'interruption': {'reason': 'user_cancel', 'message': 'constructed'},
        'query_counts': terminal['payload']['query_counts']}}
    historical = []
    for event in by_type.values():
        if event['event_type'].startswith('planning_'):
            continue
        old = deepcopy(event)
        old['schema_version'] = 1
        old['payload'].pop('execution_cursor', None)
        old['payload'].pop('planning_cycle', None)
        historical.append(old)
    assert read_json(root / 'result.json')['execution_status'] == 'completed'
    return historical + list(by_type.values())


def full_error(event):
    validator = schema.all_validators()['event', event['schema_version']]
    errors = sorted(validator.iter_errors(event), key=lambda error: str(list(error.path)))
    if not errors:
        return None
    first = errors[0]
    return f"event v{event['schema_version']} at /{'/'.join(map(str, first.path))}: {first.message}"


def test_all_actual_event_variants_retain_full_validator_admission(event_samples):
    for event in event_samples:
        assert full_error(event) is None
        assert schema.validate('event', event) is event
    for version in (1, 2):
        tags = schema._event_validators(version)
        assert {event['event_type'] for event in event_samples if event['schema_version'] == version} == set(tags)


@pytest.mark.parametrize('mutation', ['boolean_integer', 'fractional_integer', 'unknown_tag',
                                    'missing_tag', 'nonstr_tag', 'extra_property', 'wrong_payload', 'bad_timestamp'])
def test_malformed_events_keep_the_original_complete_error(event_samples, mutation):
    for sample in event_samples:
        event = deepcopy(sample)
        if mutation == 'boolean_integer':
            event['sequence'] = True
        elif mutation == 'fractional_integer':
            event['sequence'] = 1.5
        elif mutation == 'unknown_tag':
            event['event_type'] = 'unregistered'
        elif mutation == 'missing_tag':
            del event['event_type']
        elif mutation == 'nonstr_tag':
            event['event_type'] = []
        elif mutation == 'extra_property':
            event['unregistered'] = 1
        elif mutation == 'wrong_payload':
            event['payload'] = {}
        else:
            event['occurred_at_utc'] = 'tomorrow'
        expected = full_error(event)
        assert expected is not None
        with pytest.raises(DocumentError) as caught:
            schema.validate('event', event)
        assert str(caught.value) == expected


@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf, True])
def test_discriminated_ref_preserves_strict_finite_numbers(event_samples, value):
    for version in (1, 2):
        event = deepcopy(next(e for e in event_samples
                              if e['schema_version'] == version and e['event_type'] == 'query_dispatched'))
        event['payload']['query']['value'] = value
        assert full_error(event) is not None
        with pytest.raises(DocumentError) as caught:
            schema.validate('event', event)
        assert str(caught.value) == full_error(event)


@pytest.mark.parametrize('shape', ['extra_envelope_constraint', 'duplicate_discriminator'])
def test_unproven_schema_shapes_use_the_complete_validator(monkeypatch, shape):
    validators = dict(schema.all_validators())
    parent = validators['event', 2]
    changed = deepcopy(parent.schema)
    if shape == 'extra_envelope_constraint':
        changed['required'] = ['additional_contract_field']
    else:
        changed['oneOf'].append(deepcopy(changed['oneOf'][0]))
    # No dialect declaration here: retain the strict validator class while
    # constructing a hypothetical future schema for the fallback contract.
    changed.pop('$schema')
    altered = parent.evolve(schema=changed)
    altered.schema['$schema'] = parent.schema['$schema']
    validators['event', 2] = altered
    schema._event_validators.cache_clear()
    monkeypatch.setattr(schema, 'all_validators', lambda: validators)
    try:
        assert schema._event_validators(2) == {}
    finally:
        schema._event_validators.cache_clear()
