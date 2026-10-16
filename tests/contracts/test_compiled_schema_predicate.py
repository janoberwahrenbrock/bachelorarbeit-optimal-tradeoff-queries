"""Independent original-validator comparison; no solver or retained run needed."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import math

import pytest

from otqa.runtime import schema, schema_predicate, schema_reuse, schema_v1, schema_v2
from test_journal_semantic_fold import v2_events


path = Path(__file__).with_name('fixtures') / 'schema_before_reference_reuse.py'
spec = spec_from_file_location('otqa.runtime._original_compiler_reference', path)
REFERENCE = module_from_spec(spec)
spec.loader.exec_module(REFERENCE)

TARGETS = schema_reuse._PREDICATE_NAMES
REPLACEMENTS = (None, True, False, -1, 0, 1, -0., .5, 3., '', 'unknown', [], {}, [1],
    math.nan, math.inf, 10**400)


def samples():
    events, _ = v2_events(3, shortened=True, full=True)
    attempt = next(e['payload']['attempt'] for e in events if e['event_type'] == 'planning_attempt_completed'
        and e['payload']['attempt']['outcome'] == 'available')
    cycle = next(e['payload']['cycle'] for e in events if e['event_type'] == 'planning_resolved'
        and e['payload']['cycle']['outcome'] == 'available')
    plan = attempt['selected_plan']
    return {'Planning': plan, 'PlanSummary': plan['selected'],
        'ProgressEvidence': attempt['selected_progress'], 'ExecutionCursor': cycle['cursor_before'],
        'HorizonSelectionEvidence': attempt['horizon_evidence'][0], 'PlanningAttempt': attempt,
        'PlanningCycle': cycle, 'Query': plan['selected']['query'], 'Score': plan['selected']['score'],
        'PlanTree': plan['plan_tree'], 'HorizonSummary': plan['horizons'][0]}


def predicate(name):
    definitions, _ = schema_v2.definitions()
    result = schema_predicate.compile_reference(schema_v2.BASE, definitions, name)
    assert result is not None
    return result


def original(name):
    return REFERENCE.all_validators()['event', 2].evolve(
        schema={'$ref': 'urn:otqa:v2:common#/$defs/' + name})


def compare(name, value):
    positive = predicate(name)(value)
    expected = original(name).is_valid(value)
    assert not positive or expected, (name, value)
    if schema_predicate._plain_native(value):
        assert positive is expected, (name, value)


@pytest.mark.parametrize('name', TARGETS)
def test_all_seven_native_targets_compile_and_certify_original_valid_samples(name):
    value = deepcopy(samples()[name])
    assert original(name).is_valid(value)
    assert predicate(name)(value)


@pytest.mark.parametrize('name', tuple(samples()))
def test_every_property_deletion_replacement_and_extra_property_matches_reference(name):
    source = samples()[name]
    for field in source:
        missing = deepcopy(source)
        del missing[field]
        compare(name, missing)
        for replacement in REPLACEMENTS:
            changed = deepcopy(source)
            changed[field] = deepcopy(replacement)
            compare(name, changed)
    changed = deepcopy(source)
    changed['unregistered'] = 0
    compare(name, changed)


def compile_synthetic(node):
    return schema_predicate.compile_reference('urn:test:', {'Root': node}, 'Root')


@pytest.mark.parametrize('node', [{'$unknown': True}, {'format': 'date-time'},
    {'$id': 'urn:x'}, {'$dynamicRef': '#node'}, {'maxItems': 2}, {'type': ['integer', 'null']},
    {'pattern': '['}, {'additionalProperties': {'format': 'uri'}}])
def test_any_unsupported_keyword_or_invalid_pattern_declines_entire_certificate(node):
    assert compile_synthetic(node) is None


@pytest.mark.parametrize('value', [None, True, False, 0, 1, 1., -0., 2., '', [], {}, [1], [True]])
def test_oneof_anyof_enum_const_and_uniqueitems_keep_json_equality(value):
    nodes = [
        {'oneOf': [{'type': 'integer'}, {'type': 'number'}]},
        {'oneOf': [{'const': True}, {'const': 1}]},
        {'anyOf': [{'type': 'null'}, {'type': 'number', 'minimum': 0}]},
        {'enum': [True, 1, [1], {'x': False}]},
        {'const': {'x': [True, 1, -0.]}},
        {'uniqueItems': True},
    ]
    reference = REFERENCE.all_validators()['event', 2]
    for node in nodes:
        compiled = compile_synthetic(node)
        assert compiled is not None
        assert compiled(value) is reference.evolve(schema=node).is_valid(value)


@pytest.mark.parametrize('value,expected', [([True, 1], True), ([False, 0], True),
    ([1, 1.], False), ([-0., 0.], False), ([{'x': True}, {'x': 1}], True),
    ([[True], [1]], True), ([{}, {}], False)])
def test_uniqueitems_deep_bool_number_and_signedzero(value, expected):
    assert compile_synthetic({'type': 'array', 'uniqueItems': True})(value) is expected


def test_huge_integer_declines_whole_certificate_before_oneof_branching():
    node = {'oneOf': [{'type': 'integer'}, {'type': 'number'}]}
    value = 10**400
    assert REFERENCE.all_validators()['event', 2].evolve(schema=node).is_valid(value)
    assert not compile_synthetic(node)(value)
    assert original('Query').is_valid({'goal_index_a': value, 'goal_index_b': 0, 'value': 1.})
    assert not predicate('Query')({'goal_index_a': value, 'goal_index_b': 0, 'value': 1.})


@pytest.mark.parametrize('node_id', ['a', 'a\n', 'a b', '', 'a' * 129, '\ud800'])
def test_pattern_uses_search_including_dollar_final_newline(node_id):
    tree = deepcopy(samples()['PlanTree'])
    tree['node_id'] = node_id
    compare('PlanTree', tree)


def test_recursive_plan_tree_and_all_optional_fields():
    tree = deepcopy(samples()['PlanTree'])
    leaf = deepcopy(tree)
    leaf['expected_queries'] = 0.
    leaf['query'] = None
    leaf['maximum_volume_share'] = None
    leaf['stop_reason'] = 'exact_single_candidate'
    for _ in range(5):
        tree = {**deepcopy(tree), 'branches': [{'answer': '<', 'probability': .5, 'child': leaf},
            {'answer': '>', 'probability': .5, 'child': deepcopy(leaf)}]}
        compare('PlanTree', tree)
        leaf = tree


def event_outcome(reader, value):
    try:
        reader('event', value)
        return 'accepted', None
    except Exception as error:
        return type(error).__name__, str(error)


def event():
    events, _ = v2_events(2, shortened=True, full=True)
    return deepcopy(next(e for e in events if e['event_type'] == 'planning_attempt_completed'
        and e['payload']['attempt']['outcome'] == 'available'))


def test_invalid_whole_events_preserve_full_original_error_order_and_strings():
    for field in ('requested_depth', 'evaluated_horizons', 'selected_plan', 'horizon_evidence'):
        for value in REPLACEMENTS:
            changed = event()
            changed['payload']['attempt'][field] = deepcopy(value)
            assert event_outcome(schema.validate, changed) == event_outcome(REFERENCE.validate, changed)


def test_ordinary_callback_override_after_factory_delegates_before_positive_proof(monkeypatch):
    validator = schema.all_validators()['event', 2]
    failure = RuntimeError('constructed native callback override')
    def fail(*args):
        raise failure
    monkeypatch.setitem(validator.VALIDATORS, 'minimum', fail)
    with pytest.raises(RuntimeError) as captured:
        schema.validate('event', event())
    assert captured.value is failure


def test_finite_alias_override_after_factory_delegates_before_positive_proof(monkeypatch):
    schema.all_validators()
    failure = RuntimeError('constructed finite override')
    def fail(value):
        raise failure
    monkeypatch.setattr(schema_v1, '_finite', fail)
    with pytest.raises(RuntimeError) as captured:
        schema.validate('event', event())
    assert captured.value is failure


def test_pre_factory_handler_override_is_not_captured_as_native(monkeypatch):
    from jsonschema import Draft202012Validator
    failure = RuntimeError('constructed before-factory override')
    def fail(*args):
        raise failure
    schema.all_validators.cache_clear()
    schema._event_validators.cache_clear()
    try:
        with monkeypatch.context() as context:
            context.setitem(Draft202012Validator.VALIDATORS, 'minimum', fail)
            with pytest.raises(RuntimeError) as captured:
                schema.validate('event', event())
            assert captured.value is failure
    finally:
        schema.all_validators.cache_clear()
        schema._event_validators.cache_clear()


@pytest.mark.parametrize('name', ['array', 'object', 'string', 'boolean', 'null'])
def test_pre_factory_base_type_override_is_not_authorized(monkeypatch, name):
    from jsonschema import Draft202012Validator
    schema.all_validators.cache_clear()
    schema._event_validators.cache_clear()
    REFERENCE.all_validators.cache_clear()
    REFERENCE._event_validators.cache_clear()
    try:
        with monkeypatch.context() as context:
            changed = Draft202012Validator.TYPE_CHECKER.redefine(name, lambda checker, value: False)
            context.setattr(Draft202012Validator, 'TYPE_CHECKER', changed)
            document = event()
            assert event_outcome(schema.validate, document) == event_outcome(REFERENCE.validate, document)
            assert schema_reuse._CURRENT.get() is None
    finally:
        schema.all_validators.cache_clear()
        schema._event_validators.cache_clear()
        REFERENCE.all_validators.cache_clear()
        REFERENCE._event_validators.cache_clear()


class DictSubclass(dict):
    pass


@pytest.mark.parametrize('bad', [DictSubclass(), (1,), math.inf, math.nan])
def test_nonplain_or_nonfinite_values_never_receive_positive_certificate(bad):
    assert not compile_synthetic({})(bad)


def test_custom_keys_decline_before_any_compiled_lookup():
    class Key(str):
        def __eq__(self, other):
            raise AssertionError('compiled lookup on custom key')
        __hash__ = str.__hash__
    assert not compile_synthetic({'properties': {'x': {'type': 'number'}}})({Key('x'): 1})


def test_deep_or_changed_recursion_limit_declines_certificate(monkeypatch):
    compiled = compile_synthetic({})
    nested = 0
    for _ in range(25):
        nested = [nested]
    assert not compiled(nested)
    with monkeypatch.context() as context:
        context.setattr(schema_predicate.sys, 'getrecursionlimit', lambda: 500)
        assert not compiled(0)


@pytest.mark.parametrize('tail', ['A~1B', 'A/B', 'A%2FB', 'A~0B', 'A%7EB'])
def test_noncanonical_ref_and_definition_names_decline(tail):
    definitions = {'Root': {'$ref': 'urn:test:common#/$defs/' + tail}, tail: {'const': 1}}
    assert schema_predicate.compile_reference('urn:test:', definitions, 'Root') is None
