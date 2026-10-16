"""Independent combined-candidate checks; no solver or historical run fixtures."""
from copy import deepcopy

from jsonschema import Draft202012Validator, FormatChecker
import pytest

from otqa.runtime import schema, schema_reuse
from otqa.runtime.codec import DocumentError
from test_compiled_predicate_independent_review import event, full_original, outcome


REF = 'urn:otqa:v2:common#/$defs/PlanningAttempt'


def current_full_original(kind, document):
    """Use the current checker context, but no positive-call authorization."""
    assert schema_reuse._CURRENT.get() is None
    validator = schema.all_validators()[kind, document['schema_version']]
    errors = sorted(validator.iter_errors(document), key=lambda e: str(list(e.path)))
    if errors:
        first = errors[0]
        raise DocumentError(f"{kind} v2 at /{'/'.join(map(str, first.path))}: {first.message}")
    return document


@pytest.mark.parametrize('name', ['array', 'object', 'string', 'boolean', 'null'])
def test_pre_factory_non_numeric_type_overrides_keep_current_full_admission(monkeypatch, name):
    schema.all_validators.cache_clear()
    schema._event_validators.cache_clear()
    try:
        with monkeypatch.context() as context:
            checker = Draft202012Validator.TYPE_CHECKER.redefine(name, lambda _, value: False)
            context.setattr(Draft202012Validator, 'TYPE_CHECKER', checker)
            document = event()
            expected = outcome(current_full_original, document)
            assert expected != 'accepted'
            owner = schema.all_validators()['event', 2]._otqa_reference_reuse
            def forbidden(value):
                raise AssertionError('foreign type semantics must use the original reference')
            context.setitem(owner.predicates, REF, forbidden)
            assert outcome(schema.validate, document) == expected
            assert schema_reuse._CURRENT.get() is None
    finally:
        schema.all_validators.cache_clear()
        schema._event_validators.cache_clear()


def test_mutated_same_plain_document_is_not_trusted_between_calls(monkeypatch):
    document = event()
    owner = schema.all_validators()['event', 2]._otqa_reference_reuse
    native = owner.predicates[REF]
    hits = []
    def count(value):
        result = native(value)
        hits.append(result)
        return result
    monkeypatch.setitem(owner.predicates, REF, count)
    assert schema.validate('event', document) is document
    assert hits == [True]
    original = deepcopy(document['payload']['attempt']['evaluated_horizons'])
    document['payload']['attempt']['evaluated_horizons'] = [True]
    expected = outcome(full_original, document)
    assert expected != 'accepted'
    assert outcome(schema.validate, document) == expected
    assert False in hits
    document['payload']['attempt']['evaluated_horizons'] = original
    assert schema.validate('event', document) is document
    assert hits[-1] is True
    assert schema_reuse._CURRENT.get() is None


def test_valid_nonplain_nested_object_declines_certificate_but_keeps_full_acceptance(monkeypatch):
    class PlainDictSubclass(dict):
        pass
    document = event()
    document['payload']['attempt'] = PlainDictSubclass(document['payload']['attempt'])
    owner = schema.all_validators()['event', 2]._otqa_reference_reuse
    native = owner.predicates[REF]
    assert native(document['payload']['attempt']) is False
    expected = outcome(full_original, document)
    assert expected == 'accepted'
    assert outcome(schema.validate, document) == expected


def test_foreign_format_checker_context_never_inherits_native_certificate(monkeypatch):
    validators = schema.all_validators()
    validator = validators['event', 2]
    owner = validator._otqa_reference_reuse
    foreign = type(validator)(validator.schema, registry=validator._registry,
        format_checker=FormatChecker())
    def forbidden(value):
        raise AssertionError('foreign root context must use the original reference')
    monkeypatch.setitem(owner.predicates, REF, forbidden)
    monkeypatch.setitem(validators, ('event', 2), foreign)
    schema._event_validators.cache_clear()
    try:
        assert outcome(schema.validate, event()) == 'accepted'
        assert schema_reuse._CURRENT.get() is None
    finally:
        schema._event_validators.cache_clear()
