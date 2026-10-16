"""A different future event schema must use the complete reference validator."""
from copy import deepcopy
import math

import pytest
from referencing import Registry, Resource

from otqa.runtime import schema
from otqa.runtime.codec import DocumentError


DIALECT = 'https://json-schema.org/draft/2020-12/schema'


def reference_outcome(validator, document):
    errors = sorted(validator.iter_errors(document), key=lambda error: str(list(error.path)))
    if errors:
        error = errors[0]
        return ('error', f"event v2 at /{'/'.join(map(str, error.path))}: {error.message}")
    return ('accepted', document)


def optimized_outcome(document):
    try:
        return ('accepted', schema.validate('event', document))
    except DocumentError as error:
        return ('error', str(error))


@pytest.fixture
def custom_events(monkeypatch):
    native = schema.all_validators()['event', 2]

    def install(variants, *, root_id='https://example.test/root', registry=None):
        document = {'$schema': DIALECT, '$id': root_id, 'oneOf': deepcopy(variants)}
        validator = type(native)(document, registry=Registry() if registry is None else registry,
                                 format_checker=native.format_checker)
        schema._event_validators.cache_clear()
        monkeypatch.setattr(schema, 'all_validators', lambda: {('event', 2): validator})
        return validator

    yield install
    schema._event_validators.cache_clear()


@pytest.mark.parametrize('variant', [
    True,
    False,
    {'type': 'object', 'properties': {'event_type': True}},
    {'type': 'object', 'properties': {'event_type': False}},
])
def test_boolean_variant_or_property_declines_without_attribute_error(custom_events, variant):
    validator = custom_events([variant])
    document = {'schema_version': 2, 'event_type': 'example'}
    assert schema._event_validators(2) == {}
    assert optimized_outcome(document) == reference_outcome(validator, document)


def test_variant_id_cannot_resolve_payload_relative_to_the_parent(custom_events):
    def resource(url, kind):
        return Resource.from_contents({'$schema': DIALECT, '$id': url, 'type': kind})

    registry = Registry().with_resources([
        ('https://example.test/target', resource('https://example.test/target', 'integer')),
        ('https://example.test/child/target', resource('https://example.test/child/target', 'string')),
    ])
    variant = {'$id': 'child/', 'type': 'object',
        'properties': {'event_type': {'const': 'example'}, 'payload': {'$ref': 'target'}},
        'required': ['event_type', 'payload']}
    validator = custom_events([variant], registry=registry)
    assert schema._event_validators(2) == {}
    for payload in (1, 'correct child-scoped value'):
        document = {'schema_version': 2, 'event_type': 'example', 'payload': payload}
        assert optimized_outcome(document) == reference_outcome(validator, document)
    assert reference_outcome(validator, {'schema_version': 2, 'event_type': 'example', 'payload': 1})[0] == 'error'


@pytest.mark.parametrize('marker', ['$id', '$anchor', '$dynamicAnchor'])
def test_variant_resource_metadata_is_conservatively_ineligible(custom_events, marker):
    variant = {marker: 'child', 'type': 'object', 'properties': {'event_type': {'const': 'example'}}}
    validator = custom_events([variant])
    document = {'schema_version': 2, 'event_type': 'example'}
    assert schema._event_validators(2) == {}
    assert optimized_outcome(document) == reference_outcome(validator, document)


@pytest.mark.parametrize('payload', [math.nan, math.inf, -math.inf, True, 1.0, 1, '1'])
def test_explicit_variant_dialect_uses_the_full_reference_semantics(custom_events, payload):
    # An explicit dialect may select a different validator class during evolve.
    # This test requires delegation, not a new finite-number interpretation of
    # an arbitrarily changed schema; present production variants omit $schema.
    variant = {'$schema': DIALECT, 'type': 'object',
        'properties': {'event_type': {'const': 'example'}, 'payload': {'type': 'integer'}},
        'required': ['event_type', 'payload']}
    validator = custom_events([variant])
    document = {'schema_version': 2, 'event_type': 'example', 'payload': payload}
    assert schema._event_validators(2) == {}
    assert optimized_outcome(document) == reference_outcome(validator, document)


@pytest.mark.parametrize('payload,accepted', [(math.nan, False), (math.inf, False),
    (-math.inf, False), (True, False), (1.0, True), (1, True)])
def test_ordinary_selected_variant_keeps_the_native_finite_number_checker(custom_events, payload, accepted):
    variant = {'type': 'object',
        'properties': {'event_type': {'const': 'example'}, 'payload': {'type': 'number'}},
        'required': ['event_type', 'payload']}
    validator = custom_events([variant])
    selected = schema._event_validators(2)['example']
    assert selected.TYPE_CHECKER is validator.TYPE_CHECKER
    document = {'schema_version': 2, 'event_type': 'example', 'payload': payload}
    assert (optimized_outcome(document)[0] == 'accepted') is accepted
    assert optimized_outcome(document) == reference_outcome(validator, document)


def test_dict_subclass_discriminator_hooks_use_the_complete_oneof_reference(custom_events):
    class EqualToBothTags(str):
        def __eq__(self, other):
            return True

        __hash__ = str.__hash__

    class Document(dict):
        def get(self, key, default=None):
            return 'a' if key == 'event_type' else super().get(key, default)

    validator = custom_events([
        {'type': 'object', 'properties': {'event_type': {'const': tag}}, 'required': ['event_type']}
        for tag in ('a', 'b')
    ])
    document = Document(schema_version=2, event_type=EqualToBothTags('a'))
    assert reference_outcome(validator, document)[0] == 'error'
    assert optimized_outcome(document) == reference_outcome(validator, document)


def test_plain_mapping_with_ordinary_string_subclass_key_keeps_reference_semantics(custom_events):
    class Key(str):
        pass

    validator = custom_events([
        {'type': 'object', 'properties': {'event_type': {'const': tag}}, 'required': ['event_type']}
        for tag in ('a', 'b')
    ])
    document = {'schema_version': 2, Key('event_type'): 'a'}
    assert optimized_outcome(document) == reference_outcome(validator, document)
