"""Pure declarative schema checks against the complete uncached R6 reader."""
from collections import Counter
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from contextvars import copy_context
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import math

import pytest

from otqa.runtime import schema, schema_reuse
from otqa.runtime.schema_immutable import _thaw_schema
from test_journal_semantic_fold import v2_events


path = Path(__file__).with_name('fixtures') / 'schema_before_reference_reuse.py'
spec = spec_from_file_location('otqa.runtime._schema_without_reference_reuse', path)
REFERENCE = module_from_spec(spec)
spec.loader.exec_module(REFERENCE)


def copy_schema(value):
    """Explicitly copy internal read-only metadata for foreign-schema fixtures."""
    if isinstance(value, Mapping):
        return {key: copy_schema(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [copy_schema(child) for child in value]
    return value


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


class FloatSubclass(float):
    pass


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


def test_native_certificates_are_active_and_never_retain_user_data(monkeypatch):
    owner = schema.all_validators()['event', 2]._otqa_reference_reuse
    seen = []
    original = owner.predicates['urn:otqa:v2:common#/$defs/PlanningAttempt']
    def observe(value):
        context = schema_reuse._CURRENT.get()
        assert context is not None
        assert set(vars(context)) == {'namespace', 'allowed_bases', 'active',
            'validator_type', 'type_checker', 'format_checker'}
        seen.append(context)
        return original(value)
    monkeypatch.setitem(owner.predicates, 'urn:otqa:v2:common#/$defs/PlanningAttempt', observe)
    for _ in range(2):
        assert schema.validate('event', event_sample())
        assert schema_reuse._CURRENT.get() is None
    assert len(seen) == 2 and seen[0] is not seen[1]
    assert all(not context.active for context in seen)
    for obsolete in ('_exact_json', '_plain_json', '_MAX_ENTRIES', '_MAX_KEY_BYTES'):
        assert not hasattr(schema_reuse, obsolete)


def test_captured_authorization_cannot_outlive_its_validate_call(monkeypatch):
    validator = schema.all_validators()['event', 2]
    owner = validator._otqa_reference_reuse
    ref = 'urn:otqa:v2:common#/$defs/PlanningAttempt'
    original, captured = owner.predicates[ref], []
    def capture(value):
        captured.append((copy_context(), schema_reuse._CURRENT.get()))
        return original(value)
    monkeypatch.setitem(owner.predicates, ref, capture)
    assert schema.validate('event', event_sample())
    saved, authorization = captured[0]
    assert not authorization.active
    changed = validator.TYPE_CHECKER.redefine('number', lambda checker, value: False)
    monkeypatch.setattr(type(validator), 'TYPE_CHECKER', changed)
    from types import MappingProxyType
    probe = validator.evolve(schema=MappingProxyType({'$ref': ref}))
    assert not saved.run(probe.is_valid, event_sample()['payload']['attempt'])
    assert schema_reuse._CURRENT.get() is None


def test_mutation_between_calls_is_revalidated_with_original_error():
    event = event_sample()
    assert outcome(schema.validate, event)[0] == 'accepted'
    del event['payload']['attempt']['selected_plan']['selected']['query']['goal_index_b']
    expected = outcome(REFERENCE.validate, event)
    assert expected[0] != 'accepted'
    assert outcome(schema.validate, event) == expected
    assert schema_reuse._CURRENT.get() is None


def test_reentrant_public_validation_has_fresh_authorization_and_restores_parent(monkeypatch):
    owner = schema.all_validators()['event', 2]._otqa_reference_reuse
    ref = 'urn:otqa:v2:common#/$defs/PlanningAttempt'
    original = owner.predicates[ref]
    inside, parents, children = False, [], []
    def observe(value):
        nonlocal inside
        current = schema_reuse._CURRENT.get()
        if inside:
            children.append(current)
        else:
            parents.append(current)
            inside = True
            try:
                assert schema.validate('event', event_sample())
                assert schema_reuse._CURRENT.get() is current
            finally:
                inside = False
        return original(value)
    monkeypatch.setitem(owner.predicates, ref, observe)
    assert schema.validate('event', event_sample())
    assert parents and children and all(parent is not child for parent in parents for child in children)
    assert schema_reuse._CURRENT.get() is None


def test_exception_also_resets_authorization(monkeypatch):
    validator = schema.all_validators()['event', 2]
    def fail(_):
        raise RuntimeError('constructed format-check interruption')
    monkeypatch.setitem(validator.format_checker.checkers, 'date-time', (fail, ()))
    with pytest.raises(RuntimeError, match='constructed format-check'):
        schema.validate('event', event_sample())
    assert schema_reuse._CURRENT.get() is None


def test_parallel_calls_have_no_shared_validated_user_data():
    event = event_sample()
    with ThreadPoolExecutor(max_workers=4) as pool:
        actual = list(pool.map(lambda _: outcome(schema.validate, deepcopy(event)), range(16)))
    assert actual == [('accepted', None)] * 16
    assert schema_reuse._CURRENT.get() is None


def test_unknown_evolved_schema_scope_falls_back_without_certificates(monkeypatch):
    validators = dict(schema.all_validators())
    parent = validators['event', 2]
    changed = _thaw_schema(parent.schema)
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
