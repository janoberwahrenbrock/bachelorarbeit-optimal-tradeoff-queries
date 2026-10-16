"""Independent narrow adversarial contexts; no solver or external artifact."""
from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from otqa.runtime import schema, schema_reuse
from otqa.runtime.codec import DocumentError
from test_schema_reference_reuse import event_sample


def outcome(document, *, full=False, validator=None):
    try:
        if full:
            errors = sorted(validator.iter_errors(document), key=lambda error: str(list(error.path)))
            if errors:
                error = errors[0]
                raise DocumentError(f"event v{document['schema_version']} at /{'/'.join(map(str, error.path))}: {error.message}")
        else:
            schema.validate('event', document)
        return ('accepted', None)
    except Exception as error:
        return type(error).__name__, str(error)


def count_original_references(monkeypatch):
    owner = schema.all_validators()['event', 2]._otqa_reference_reuse
    original = owner.original_ref
    calls = []

    def observe(validator, ref, instance, subschema):
        if ref.endswith('/Planning') or ref.endswith('/PlanSummary'):
            calls.append((ref, schema_reuse._CURRENT.get()))
        yield from original(validator, ref, instance, subschema)

    monkeypatch.setattr(owner, 'original_ref', observe)
    return calls


def test_validator_without_factory_metadata_retains_full_admission_and_error(monkeypatch):
    validator = Draft202012Validator({'$schema': schema.DIALECT, '$id': 'urn:unknown:event', 'oneOf': [
        {'type': 'object', 'properties': {'event_type': {'const': 'example'}, 'payload': {'type': 'integer'}},
         'required': ['event_type', 'payload']}]})
    assert not hasattr(validator, '_otqa_reference_reuse')
    monkeypatch.setattr(schema, 'all_validators', lambda: {('event', 2): validator})
    schema._event_validators.cache_clear()
    try:
        for payload in (1, True, '1'):
            document = {'schema_version': 2, 'event_type': 'example', 'payload': payload}
            assert outcome(document) == outcome(document, full=True, validator=validator)
            assert schema_reuse._CURRENT.get() is None
    finally:
        schema._event_validators.cache_clear()


def test_changed_transitive_definition_uses_complete_ref_checks(monkeypatch):
    validator = schema.all_validators()['event', 2]
    query = validator._resolver.lookup('urn:otqa:v2:common#/$defs/Query').contents
    original = deepcopy(query)
    calls = count_original_references(monkeypatch)
    try:
        query['properties']['value']['minimum'] = 100.0
        document = event_sample()
        expected = outcome(document, full=True, validator=validator)
        calls.clear()
        assert expected[0] != 'accepted'
        assert outcome(document) == expected
        assert calls and all(context is None for _, context in calls)
        assert schema_reuse._CURRENT.get() is None
    finally:
        query.clear()
        query.update(original)


def test_foreign_format_checker_is_not_a_factory_context(monkeypatch):
    validator = schema.all_validators()['event', 2]
    # Evolve with an explicit $schema would select the default jsonschema class.
    # Keep the actual strict factory class here to isolate format-context reuse.
    changed = type(validator)(validator.schema, registry=validator._registry,
                              format_checker=FormatChecker())
    validators = dict(schema.all_validators())
    validators['event', 2] = changed
    calls = count_original_references(monkeypatch)
    monkeypatch.setattr(schema, 'all_validators', lambda: validators)
    schema._event_validators.cache_clear()
    try:
        document = event_sample()
        assert outcome(document) == outcome(document, full=True, validator=changed)
        assert calls and all(context is None for _, context in calls)
        assert schema_reuse._CURRENT.get() is None
    finally:
        schema._event_validators.cache_clear()


def test_replaced_type_checker_is_not_a_factory_context(monkeypatch):
    validator = schema.all_validators()['event', 2]
    native_class = type(validator)
    different = validator.TYPE_CHECKER.redefine('integer', lambda checker, value: type(value) is int)
    calls = count_original_references(monkeypatch)
    monkeypatch.setattr(native_class, 'TYPE_CHECKER', different)
    document = event_sample()
    assert outcome(document) == outcome(document, full=True, validator=validator)
    assert calls and all(context is None for _, context in calls)
    assert schema_reuse._CURRENT.get() is None


@pytest.mark.parametrize('tag', [[], {}, [1], {'tag': 'x'}, None, 1, True,
                                (), bytearray(b'event'), float('nan')])
def test_malformed_or_nonjson_discriminator_preserves_complete_error(tag):
    document = event_sample()
    document['event_type'] = tag
    validator = schema.all_validators()['event', 2]
    expected = outcome(document, full=True, validator=validator)
    assert expected[0] != 'accepted'
    assert outcome(document) == expected
    assert schema_reuse._CURRENT.get() is None


def test_early_close_and_error_never_remember_partial_reference_success():
    class Resolver:
        _base_uri = 'urn:otqa:v2:common'

        def lookup(self, ref):
            return type('Resolved', (), {'contents': target, 'resolver': self})()

        _registry = object()

    class Validator:
        _ref_resolver = None
        _resolver = Resolver()
        TYPE_CHECKER = object()
        format_checker = object()

    target = {}
    ref = 'urn:otqa:v2:common#/$defs/Planning'
    error = RuntimeError('original interruption')

    def original(validator, reference, instance, subschema):
        yield 'first original error'
        raise error

    owner = schema_reuse.ReferenceReuse(original)
    owner.targets[ref] = target
    context = schema_reuse._ValidationCall(owner.namespace, frozenset((Resolver._base_uri,)))
    token = schema_reuse._CURRENT.set(context)
    try:
        iterator = owner.reference(Validator(), ref, {}, {'$ref': ref})
        assert next(iterator) == 'first original error'
        iterator.close()
        assert not context.successes
        iterator = owner.reference(Validator(), ref, {}, {'$ref': ref})
        assert next(iterator) == 'first original error'
        with pytest.raises(RuntimeError) as caught:
            next(iterator)
        assert caught.value is error
        assert not context.successes
    finally:
        schema_reuse.end_call(token)
    assert schema_reuse._CURRENT.get() is None
