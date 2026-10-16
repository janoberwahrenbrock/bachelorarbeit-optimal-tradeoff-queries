"""Compiled native metadata is immutable; full R7 document semantics remain."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import MappingProxyType, ModuleType
import math
import sys

import pytest

from otqa.runtime import schema, schema_reuse
from otqa.runtime.schema_immutable import _compile_schema, _SchemaSequence
from test_journal_semantic_fold import v2_events
from test_schema_reference_reuse import event_sample


# Byte-frozen R7 schema+reuse modules, loaded as a separate package without any
# monkeypatch of the product import namespace. Raw builders/codec are unchanged.
package_name = '_otqa_r7_schema_reference'
package = ModuleType(package_name)
package.__path__ = [str(Path(schema.__file__).parent)]
sys.modules[package_name] = package
for name, filename in [('schema_reuse', 'schema_reuse_before_immutable.py'), ('schema', 'schema_before_immutable.py')]:
    path = Path(__file__).with_name('fixtures') / filename
    spec = spec_from_file_location(package_name + '.' + name, path)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
REFERENCE = module


def outcome(reader, kind, document):
    try:
        reader(kind, document)
        return 'accepted', None
    except Exception as error:
        return type(error).__name__, str(error)


def plain(value):
    if type(value) is MappingProxyType:
        return {key: plain(child) for key, child in value.items()}
    if type(value) is _SchemaSequence:
        return [plain(child) for child in value]
    return value


def assert_frozen(value):
    if type(value) is MappingProxyType:
        for child in value.values():
            assert_frozen(child)
    elif type(value) is _SchemaSequence:
        for child in value:
            assert_frozen(child)
    else:
        assert value is None or type(value) in (str, bool, int, float)
        assert type(value) is not float or math.isfinite(value)


def test_all_roots_and_complete_common_resources_are_deeply_frozen():
    for validator in schema.all_validators().values():
        assert type(validator.schema) is MappingProxyType
        assert_frozen(validator.schema)
    validator = schema.all_validators()['event', 2]
    for version in (1, 2):
        common = validator._resolver.lookup(f'urn:otqa:v{version}:common').contents
        assert type(common) is MappingProxyType
        assert_frozen(common)
        with pytest.raises(TypeError):
            common['$defs'] = {}
        with pytest.raises(TypeError):
            common['$defs']['Query']['type'] = 'broken'


def test_compilation_has_no_mutable_builder_alias_or_container_escape():
    raw = {'outer': [{'enum': ['a', 'b']}]}
    sealed = _compile_schema(raw)
    raw['outer'][0]['enum'][0] = 'changed'
    assert sealed['outer'][0]['enum'][0] == 'a'
    for mutation in [lambda: dict.__setitem__(sealed, 'x', 1),
        lambda: dict.__setitem__(sealed['outer'][0], 'x', 1),
        lambda: list.__setitem__(sealed['outer'], 0, 1),
        lambda: object.__setattr__(sealed['outer'], 'x', 1),
        lambda: object.__setattr__(sealed, 'x', 1),
        lambda: object.__setattr__(sealed['outer'], '__class__', ForeignTuple),
        lambda: object.__dict__['__class__'].__set__(sealed['outer'], ForeignTuple)]:
        with pytest.raises((TypeError, AttributeError)):
            mutation()
    copy = sealed.copy()
    copy['outer'] = 'replacement'
    assert type(sealed['outer']) is _SchemaSequence
    assert type(sealed['outer'][0]['enum']) is tuple


class ForeignTuple(tuple):
    __slots__ = ()

    def __iter__(self):
        return iter(('changed',))


@pytest.mark.parametrize('bad', [(), set(), b'x', bytearray(b'x'), math.nan, math.inf, {1: 'x'}])
def test_unknown_metadata_is_rejected_before_native_compilation(bad):
    with pytest.raises(TypeError):
        _compile_schema({'nested': bad})


def test_unknown_metadata_callbacks_and_cycles_are_never_traversed():
    calls = []
    class Foreign(dict):
        def items(self):
            calls.append('items')
            raise AssertionError('called user items')
    class Buffer:
        def __buffer__(self, flags):
            calls.append('buffer')
            return memoryview(b'x')
    for value in [Foreign(x=1), Buffer()]:
        with pytest.raises(TypeError):
            _compile_schema({'x': value})
    cycle = {}
    cycle['self'] = cycle
    with pytest.raises(ValueError, match='cycle'):
        _compile_schema(cycle)
    assert not calls


def test_valid_and_invalid_analytic_event_admissions_and_errors_match_r7():
    for depth in (1, 2, 3):
        events, _ = v2_events(depth, shortened=True, full=True)
        for event in events:
            documents = [event]
            for key, bad in [('event_type', []), ('sequence', True), ('schema_version', '2')]:
                changed = deepcopy(event)
                changed[key] = bad
                documents.append(changed)
            changed = deepcopy(event)
            changed['extra_unregistered_property'] = None
            documents.append(changed)
            for document in documents:
                assert outcome(schema.validate, 'event', document) == outcome(REFERENCE.validate, 'event', document)
    assert schema_reuse._CURRENT.get() is None


def test_native_enum_diagnostic_and_raw_builder_contract_match_r7():
    for (kind, version), original in REFERENCE.all_validators().items():
        assert plain(schema.all_validators()[kind, version].schema) == original.schema
    raw = schema.versioned_definitions(2)[1]['config']
    assert type(raw) is dict
    # Common's enum is still displayed using the historical list spelling.
    validator = schema.all_validators()['config', 2]
    definitions = validator._resolver.lookup('urn:otqa:v2:common').contents['$defs']
    algorithms = [definition for definition in definitions.values() if 'properties' in definition
                  and 'horizon_execution' in definition['properties']]
    assert algorithms
    for algorithm in algorithms:
        assert type(algorithm['properties']['horizon_execution']['enum']) is _SchemaSequence
        assert algorithm['properties']['horizon_execution']['enum'] == ('receding', 'countdown')


def test_every_known_native_enum_retains_the_complete_original_error():
    native = schema.all_validators()['event', 2]
    original = REFERENCE.all_validators()['event', 2]
    owner = native._otqa_reference_reuse
    assert owner.enum_schemas
    for node in owner.enum_schemas.values():
        # Native enum literals are strings; no proxy repr is substituted for a
        # historical object literal. This guards future schema extensions too.
        assert all(type(value) is str for value in node['enum'])
        compiled = type(native)(node, registry=native._registry, format_checker=native.format_checker)
        raw = type(original)(plain(node), registry=original._registry, format_checker=original.format_checker)
        document = '__not_a_native_enum_value__'
        expected = [error.message for error in raw.iter_errors(document)]
        assert expected and [error.message for error in compiled.iter_errors(document)] == expected


@pytest.mark.parametrize('frozen', [False, True])
def test_unknown_external_root_retains_full_ref_checks_without_memo(monkeypatch, frozen):
    validators = dict(schema.all_validators())
    parent = validators['event', 2]
    unknown = plain(parent.schema)
    unknown.pop('$schema')
    unknown['$id'] = 'urn:unknown:external-schema'
    if frozen:
        unknown = _compile_schema(unknown)
    altered = type(parent)(unknown, registry=parent._registry, format_checker=parent.format_checker)
    validators['event', 2] = altered
    owner = parent._otqa_reference_reuse
    original, calls = owner.original_ref, []
    def observe(validator, ref, instance, subschema):
        if ref.endswith('/Planning'):
            calls.append(schema_reuse._CURRENT.get())
        yield from original(validator, ref, instance, subschema)
    monkeypatch.setattr(owner, 'original_ref', observe)
    monkeypatch.setattr(schema, 'all_validators', lambda: validators)
    schema._event_validators.cache_clear()
    try:
        document = event_sample()
        assert outcome(schema.validate, 'event', document) == ('accepted', None)
        assert len(calls) > 1 and all(call is None for call in calls)
    finally:
        schema._event_validators.cache_clear()
    assert schema_reuse._CURRENT.get() is None


def test_native_event_dispatch_and_positive_certificates_remain_enabled(monkeypatch):
    assert set(schema._event_validators(2)) == set(REFERENCE._event_validators(2))
    owner = schema.all_validators()['event', 2]._otqa_reference_reuse
    ref = 'urn:otqa:v2:common#/$defs/PlanningAttempt'
    original, calls = owner.predicates[ref], []
    def observe(value):
        calls.append(schema_reuse._CURRENT.get())
        return original(value)
    monkeypatch.setitem(owner.predicates, ref, observe)
    for _ in range(2):
        assert schema.validate('event', event_sample())
    assert len(calls) == 2 and all(call is not None for call in calls)
    assert calls[0] is not calls[1] and schema_reuse._CURRENT.get() is None
