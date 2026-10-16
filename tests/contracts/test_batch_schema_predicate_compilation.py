"""Construction-only sharing of fully compiled schema closures; no solver."""
from copy import deepcopy
from unittest.mock import patch

import pytest

from otqa.runtime import schema_predicate, schema_reuse, schema_v2
from otqa.runtime.schema_immutable import _compile_schema
from test_compiled_schema_predicate import REPLACEMENTS, samples


def test_native_seven_targets_share_one_complete_definition_table():
    definitions, _ = schema_v2.definitions()
    created = []
    original = schema_predicate._Compiler.__init__

    def capture(self, base, defs):
        original(self, base, defs)
        created.append(self)

    with patch.object(schema_predicate._Compiler, '__init__', capture):
        result = schema_predicate.compile_references(
            schema_v2.BASE, definitions, schema_reuse._PREDICATE_NAMES)
    assert result is not None
    assert len(created) == 1
    assert created[0].failed is False
    assert all(slot[0] is not None for _, slot in created[0].definitions_compiled.values())
    assert set(result) == set(schema_reuse._PREDICATE_NAMES)
    assert len({id(check) for check in result.values()}) == 7


@pytest.mark.parametrize('name', schema_reuse._PREDICATE_NAMES)
def test_complete_native_target_mutations_match_independent_compilation(name):
    definitions, _ = schema_v2.definitions()
    batch = schema_predicate.compile_references(
        schema_v2.BASE, definitions, schema_reuse._PREDICATE_NAMES)[name]
    separate = schema_predicate.compile_reference(schema_v2.BASE, definitions, name)
    value = samples()[name]
    assert batch(value) is separate(value) is True
    for field in value:
        missing = deepcopy(value)
        del missing[field]
        assert batch(missing) is separate(missing)
        for replacement in REPLACEMENTS:
            changed = deepcopy(value)
            changed[field] = replacement
            assert batch(changed) is separate(changed)


def test_recursive_shared_definition_is_compiled_once():
    base = schema_v2.BASE
    ref = base + 'common#/$defs/'
    definitions = {
        'Leaf': {'type': 'integer'},
        'Tree': {'anyOf': [{'$ref': ref + 'Leaf'}, {'type': 'array',
            'items': {'$ref': ref + 'Tree'}}]},
        'First': {'$ref': ref + 'Tree'},
        'Second': {'$ref': ref + 'Tree'},
    }
    visits = {}
    original = schema_predicate._Compiler.node

    def count(self, node):
        visits[id(node)] = visits.get(id(node), 0) + 1
        return original(self, node)

    with patch.object(schema_predicate._Compiler, 'node', count):
        result = schema_predicate.compile_references(base, definitions, ('First', 'Second'))
    assert result is not None
    assert all(visits[id(node)] == 1 for node in definitions.values())
    for value in (1, [], [1, [2, []]], [False], ['bad']):
        assert result['First'](value) is result['Second'](value)
        assert result['First'](value) is schema_predicate.compile_reference(
            base, definitions, 'First')(value)


def test_unsupported_target_discards_batch_and_keeps_independent_target_support():
    definitions = {'Planning': {'type': 'string', 'minLength': 1},
        'PlanSummary': {'const': 1}}
    assert schema_predicate.compile_references(
        schema_v2.BASE, definitions, ('PlanSummary', 'Planning')) is None
    owner = schema_reuse.ReferenceReuse(None)
    with patch.object(schema_reuse, 'compile_reference', wraps=schema_predicate.compile_reference) as individual:
        owner.register_family(schema_v2.BASE, _compile_schema(definitions))
    assert [call.args[2] for call in individual.call_args_list] == ['Planning', 'PlanSummary']
    assert owner.predicates[schema_v2.BASE + 'common#/$defs/Planning'] is None
    summary = owner.predicates[schema_v2.BASE + 'common#/$defs/PlanSummary']
    assert summary(1) is True
    assert summary(2) is False


@pytest.mark.parametrize('exception', [TypeError, ValueError, RecursionError])
def test_partial_compilation_failure_returns_no_predicate_mapping(exception):
    definitions = {'First': {'const': 1}, 'Second': {'const': 2}}
    original = schema_predicate._Compiler.definition

    def fail_second(self, name):
        if name == 'Second':
            raise exception('unsupported construction')
        return original(self, name)

    with patch.object(schema_predicate._Compiler, 'definition', fail_second):
        assert schema_predicate.compile_references(
            schema_v2.BASE, definitions, ('First', 'Second')) is None


def test_certificate_domain_and_no_user_data_state_match_existing_wrapper():
    definitions = {'First': {}, 'Second': {'type': 'array'}}
    result = schema_predicate.compile_references(schema_v2.BASE, definitions, ('First', 'Second'))
    cycle = []
    cycle.append(cycle)
    class CustomDict(dict):
        pass
    for value in (cycle, CustomDict(), float('nan'), float('inf'), 10**400):
        for name in definitions:
            assert result[name](value) is schema_predicate.compile_reference(
                schema_v2.BASE, definitions, name)(value) is False
    for name in definitions:
        assert len(result[name].__closure__) == 1
