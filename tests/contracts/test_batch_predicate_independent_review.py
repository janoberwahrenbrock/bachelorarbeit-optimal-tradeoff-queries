"""Independent, solver-free checks of shared static compiler construction."""
from copy import deepcopy

from jsonschema import Draft202012Validator
import pytest

from otqa.runtime import schema_predicate, schema_reuse, schema_v2
from otqa.runtime.schema_immutable import _compile_schema


BASE = 'urn:otqa:v2:'
PREFIX = BASE + 'common#/$defs/'


def test_overlapping_reference_is_compiled_once_without_cross_target_admission(monkeypatch):
    definitions = {
        'Leaf': {'type': 'integer', 'minimum': 0},
        'Array': {'type': 'array', 'items': {'$ref': PREFIX + 'Leaf'}},
        'Object': {'type': 'object', 'properties': {'value': {'$ref': PREFIX + 'Leaf'}},
            'required': ['value'], 'additionalProperties': False},
    }
    original, hits = schema_predicate._Compiler.node, []
    def count(self, node):
        if node is definitions['Leaf']:
            hits.append(id(self))
        return original(self, node)
    with monkeypatch.context() as context:
        context.setattr(schema_predicate._Compiler, 'node', count)
        batch = schema_predicate.compile_references(BASE, definitions, ['Array', 'Object'])
    assert len(hits) == 1
    assert batch['Array'] is not batch['Object']
    for name in ('Array', 'Object'):
        independent = schema_predicate.compile_reference(BASE, definitions, name)
        for value in [0, -1, True, [], [1], [True], {}, {'value': 1}, {'value': -1}]:
            assert batch[name](value) == independent(value)


@pytest.mark.parametrize('failure', [ValueError('synthetic compile failure'),
    RecursionError('synthetic compile depth')])
def test_batch_exception_exports_no_partial_success_and_does_not_poison_later_compile(monkeypatch, failure):
    definitions = {'Good': {'type': 'integer'}, 'Bad': {'type': 'object'}}
    original = schema_predicate._Compiler.node
    def fail(self, node):
        if node is definitions['Bad']:
            raise failure
        return original(self, node)
    with monkeypatch.context() as context:
        context.setattr(schema_predicate._Compiler, 'node', fail)
        assert schema_predicate.compile_references(BASE, definitions, ['Good', 'Bad']) is None
    good = schema_predicate.compile_reference(BASE, definitions, 'Good')
    assert good(1) and not good(True)


def test_unsupported_family_discards_batch_but_keeps_independent_supported_targets(monkeypatch):
    definitions, _ = schema_v2.definitions()
    definitions = deepcopy(definitions)
    definitions['Planning']['not'] = {}  # Unsupported by complete certificates.
    owner = schema_reuse.ReferenceReuse(Draft202012Validator.VALIDATORS['$ref'],
        Draft202012Validator.VALIDATORS['enum'])
    original, calls = schema_reuse.compile_reference, []
    def independent(base, defs, name):
        calls.append(name)
        return original(base, defs, name)
    monkeypatch.setattr(schema_reuse, 'compile_reference', independent)
    owner.register_family(BASE, _compile_schema(definitions))
    assert tuple(calls) == schema_reuse._PREDICATE_NAMES
    assert owner.predicates[PREFIX + 'Planning'] is None
    cursor = owner.predicates[PREFIX + 'ExecutionCursor']
    assert cursor({'answered_total': 0, 'remaining_depth': 2})
    assert not cursor({'answered_total': True, 'remaining_depth': 2})
    assert len(owner.targets) == len(schema_reuse._PREDICATE_NAMES)


def test_batch_certifiers_remain_pure_after_same_document_mutation():
    definitions = {'A': {'type': 'array', 'items': {'type': 'integer'}},
        'B': {'$ref': PREFIX + 'A'}}
    batch = schema_predicate.compile_references(BASE, definitions, ['A', 'B'])
    document = [1]
    assert batch['A'](document) and batch['B'](document)
    document[0] = True
    assert not batch['A'](document) and not batch['B'](document)
    document[0] = -0
    assert batch['A'](document) and batch['B'](document)
