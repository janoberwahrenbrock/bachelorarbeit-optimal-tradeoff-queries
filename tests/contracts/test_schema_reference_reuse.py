"""Pure declarative schema checks against the complete uncached R6 reader."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import math

import pytest

from otqa.runtime import schema, schema_reuse
from test_journal_semantic_fold import v2_events


path = Path(__file__).with_name('fixtures') / 'schema_before_reference_reuse.py'
spec = spec_from_file_location('otqa.runtime._schema_without_reference_reuse', path)
REFERENCE = module_from_spec(spec)
spec.loader.exec_module(REFERENCE)


def event_sample():
    events, _ = v2_events(3, shortened=True, full=True)
    return deepcopy(next(e for e in events if e['event_type'] == 'planning_attempt_completed'
                         and e['payload']['attempt']['outcome'] == 'available'))


def outcome(reader, value):
    try:
        reader('event', value)
        return 'accepted', None
    except Exception as error:
        return type(error).__name__, str(error)


def observed(monkeypatch):
    owner = schema.all_validators()['event', 2]._otqa_reference_reuse
    original = owner.original_ref
    calls = Counter()
    def track(validator, ref, instance, subschema):
        if ref.endswith('/Planning') or ref.endswith('/PlanSummary'):
            calls[ref.rsplit('/', 1)[-1]] += 1
        yield from original(validator, ref, instance, subschema)
    monkeypatch.setattr(owner, 'original_ref', track)
    return calls


def test_equal_successful_refs_reused_only_within_each_validate(monkeypatch):
    calls = observed(monkeypatch)
    event = event_sample()
    for index in range(1, 4):
        assert schema.validate('event', event) is event
        assert calls == {'Planning': index, 'PlanSummary': index}
        assert schema_reuse._CURRENT.get() is None


def test_direct_full_validator_retains_complete_validation_without_call_context(monkeypatch):
    calls = observed(monkeypatch)
    assert schema.all_validators()['event', 2].is_valid(event_sample())
    assert calls['Planning'] > 1 and calls['PlanSummary'] > 1
    assert schema_reuse._CURRENT.get() is None


@pytest.mark.parametrize('value', [None, True, False, 0, 0., -0., 1, 1., 'a', [], {}])
def test_plain_json_exact_types_have_distinct_keys(value):
    encoded = schema_reuse._exact_json(value)
    assert encoded is not None
    assert schema_reuse._CURRENT.get() is None


def test_integer_float_bool_and_zero_keys_do_not_alias():
    values = [True, 1, 1., False, 0, 0., -0.]
    assert len({schema_reuse._exact_json(value) for value in values}) == len(values)


class DictSubclass(dict):
    pass


class ListSubclass(list):
    pass


class FloatSubclass(float):
    pass


class StringSubclass(str):
    pass


@pytest.mark.parametrize('tag', [[], {}, StringSubclass('planning_attempt_completed')])
def test_nonplain_event_tag_retains_full_reader_outcome(tag):
    event = event_sample()
    event['event_type'] = tag
    assert outcome(schema.validate, event) == outcome(REFERENCE.validate, event)
    assert schema_reuse._CURRENT.get() is None


@pytest.mark.parametrize('value', [(1, 2), DictSubclass(a=1), ListSubclass([1]), FloatSubclass(1.),
    StringSubclass('x'), {1: 'x'}, {StringSubclass('x'): 1}, math.nan, math.inf, -math.inf])
def test_unsupported_types_fall_back_without_cache_keys(value):
    assert schema_reuse._exact_json(value) is None


def test_cyclic_nonjson_value_has_no_key():
    value = []
    value.append(value)
    assert schema_reuse._exact_json(value) is None


@pytest.mark.parametrize('change', ['bool_horizon', 'float_horizon', 'missing_query', 'nan', 'inf',
    'wrong_score', 'tuple_array', 'float_subclass', 'extra_property', 'different_zero'])
def test_invalid_or_type_distinct_duplicate_is_fully_checked(change):
    event = event_sample()
    selected = event['payload']['attempt']['horizon_evidence'][0]['selected_plan']['selected']
    if change == 'bool_horizon':
        selected['horizon'] = True
    elif change == 'float_horizon':
        selected['horizon'] = 3.
    elif change == 'missing_query':
        del selected['query']['goal_index_b']
    elif change == 'nan':
        selected['query']['value'] = math.nan
    elif change == 'inf':
        selected['query']['value'] = math.inf
    elif change == 'wrong_score':
        selected['score']['kind'] = 'invalid'
    elif change == 'tuple_array':
        selected['score']['lexicographic_expected_values'] = (1.5,)
    elif change == 'float_subclass':
        selected['query']['value'] = FloatSubclass(1.)
    elif change == 'extra_property':
        selected['query']['unregistered'] = 1
    else:
        selected['query']['value'] = -0.
    expected = outcome(REFERENCE.validate, event)
    assert outcome(schema.validate, event) == expected
    assert schema_reuse._CURRENT.get() is None


def test_mutation_between_calls_cannot_reuse_an_earlier_success():
    event = event_sample()
    assert outcome(schema.validate, event)[0] == 'accepted'
    del event['payload']['attempt']['selected_plan']['selected']['query']['goal_index_b']
    expected = outcome(REFERENCE.validate, event)
    assert expected[0] != 'accepted'
    assert outcome(schema.validate, event) == expected
    assert schema_reuse._CURRENT.get() is None


@pytest.mark.parametrize('entries,bytes_limit', [(0, 0), (1, 512), (2, 2048), (64, 512 * 1024)])
def test_budget_exhaustion_only_returns_to_complete_validation(monkeypatch, entries, bytes_limit):
    monkeypatch.setattr(schema_reuse, '_MAX_ENTRIES', entries)
    monkeypatch.setattr(schema_reuse, '_MAX_KEY_BYTES', bytes_limit)
    calls = []
    original = schema_reuse._ValidationCall
    class Recorded(original):
        def __init__(self, *args):
            super().__init__(*args)
            calls.append(self)
    monkeypatch.setattr(schema_reuse, '_ValidationCall', Recorded)
    assert outcome(schema.validate, event_sample()) == ('accepted', None)
    assert calls and all(len(call.successes) <= entries and call.key_bytes <= bytes_limit for call in calls)
    assert schema_reuse._CURRENT.get() is None


def test_reentrant_validation_has_distinct_context_and_restores_its_caller(monkeypatch):
    owner = schema.all_validators()['event', 2]._otqa_reference_reuse
    original = owner.original_ref
    inside = False
    calls = []
    def reentrant(validator, ref, instance, subschema):
        nonlocal inside
        if not inside:
            inside = True
            before = schema_reuse._CURRENT.get()
            calls.append(before)
            assert schema.validate('event', event_sample())
            assert schema_reuse._CURRENT.get() is before
            inside = False
        else:
            assert schema_reuse._CURRENT.get() is not calls[-1]
        yield from original(validator, ref, instance, subschema)
    monkeypatch.setattr(owner, 'original_ref', reentrant)
    assert schema.validate('event', event_sample())
    assert calls and schema_reuse._CURRENT.get() is None


def test_exception_also_resets_call_context(monkeypatch):
    validator = schema.all_validators()['event', 2]
    def fail(_):
        raise RuntimeError('constructed format-check interruption')
    monkeypatch.setitem(validator.format_checker.checkers, 'date-time', (fail, ()))
    with pytest.raises(RuntimeError, match='constructed format-check'):
        schema.validate('event', event_sample())
    assert schema_reuse._CURRENT.get() is None


def test_parallel_calls_never_share_success_entries():
    event = event_sample()
    with ThreadPoolExecutor(max_workers=4) as pool:
        actual = list(pool.map(lambda _: outcome(schema.validate, deepcopy(event)), range(16)))
    assert actual == [('accepted', None)] * 16
    assert schema_reuse._CURRENT.get() is None


def test_unknown_evolved_schema_scope_falls_back_without_reuse(monkeypatch):
    validators = dict(schema.all_validators())
    parent = validators['event', 2]
    changed = deepcopy(parent.schema)
    changed.pop('$schema')
    changed['$id'] = 'urn:custom:untrusted-scope'
    validators['event', 2] = parent.evolve(schema=changed)
    calls = observed(monkeypatch)
    monkeypatch.setattr(schema, 'all_validators', lambda: validators)
    schema._event_validators.cache_clear()
    try:
        assert schema.validate('event', event_sample())
        assert calls['Planning'] > 1 and calls['PlanSummary'] > 1
        assert schema_reuse._CURRENT.get() is None
    finally:
        schema._event_validators.cache_clear()


def test_unknown_transient_resolver_preserves_the_first_original_error(monkeypatch):
    class ForeignResolver:
        def __init__(self, delegate, calls):
            self.delegate, self.calls = delegate, calls

        def __getattr__(self, name):
            return getattr(self.delegate, name)

        def in_subresource(self, resource):
            return type(self)(self.delegate.in_subresource(resource), self.calls)

        def lookup(self, ref):
            self.calls.append(ref)
            if len(self.calls) == 1:
                raise RuntimeError('foreign first lookup')
            return self.delegate.lookup(ref)

    outcomes = []
    for reader in (REFERENCE, schema):
        validators = dict(reader.all_validators())
        parent = validators['event', 2]
        calls = []
        validators['event', 2] = parent.evolve(_resolver=ForeignResolver(parent._resolver, calls))
        with monkeypatch.context() as context:
            context.setattr(reader, 'all_validators', lambda: validators)
            reader._event_validators.cache_clear()
            try:
                outcomes.append(outcome(reader.validate, event_sample()))
                assert len(calls) == 1
                assert schema_reuse._CURRENT.get() is None
            finally:
                reader._event_validators.cache_clear()
    assert outcomes == [('RuntimeError', 'foreign first lookup')] * 2


def test_v1_repeated_plan_summary_is_also_scoped_and_strict():
    event = event_sample()
    old = {**event, 'schema_version': 1, 'event_type': 'query_planned',
        'payload': {'state_before_index': 0, 'planning': event['payload']['attempt']['selected_plan']}}
    old['numeric_hex'] = {}
    assert outcome(schema.validate, old) == outcome(REFERENCE.validate, old) == ('accepted', None)
    old['payload']['planning']['horizons'][0]['plan']['horizon'] = True
    assert outcome(schema.validate, old) == outcome(REFERENCE.validate, old)
