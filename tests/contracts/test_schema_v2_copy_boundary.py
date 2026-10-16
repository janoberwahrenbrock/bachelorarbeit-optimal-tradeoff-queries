"""The version rewrite owns its JSON containers without an outer deepcopy."""
from copy import deepcopy
from pathlib import Path

import pytest

import otqa
from otqa.runtime import schema, schema_v1, schema_v2
from otqa.runtime.schema_immutable import _compile_schema, _thaw_schema


def assert_native_metadata(value):
    if type(value) is dict:
        assert all(type(key) is str for key in value)
        for child in value.values():
            assert_native_metadata(child)
    elif type(value) in (list, tuple):
        for child in value:
            assert_native_metadata(child)
    else:
        assert value is None or type(value) in (bool, str, int, float)


def test_actual_legacy_metadata_has_only_supported_json_values():
    assert_native_metadata(schema_v1.definitions())


def test_all_40_resource_bytes_and_38_compiled_roots_remain_exact(tmp_path):
    names = schema.write_schema_resources(tmp_path)
    installed = Path(otqa.__file__).parent / 'schemas'
    assert len(names) == 40
    for path in tmp_path.iterdir():
        assert path.read_bytes() == (installed / path.name).read_bytes()
    validators = schema.all_validators()
    assert len(validators) == 38
    for validator in validators.values():
        view = _thaw_schema(validator.schema)
        validator.check_schema(view)


def test_rewrite_boundary_copies_every_nested_injected_json_container(monkeypatch):
    definitions, docs = schema_v1.definitions()
    shared = {'nested': [{'value': 7, '$ref': schema_v1.BASE + 'common#/$defs/Query'}]}
    definitions['Query']['copy_a'] = shared
    definitions['Query']['copy_b'] = shared
    source = definitions, docs
    before = deepcopy(source)
    monkeypatch.setattr(schema_v2.old, 'definitions', lambda: source)
    first, _ = schema_v2.definitions()
    second, _ = schema_v2.definitions()
    assert source == before
    assert first['Query']['copy_a'] is not shared
    assert first['Query']['copy_a'] is not first['Query']['copy_b']
    first['Query']['copy_a']['nested'][0]['value'] = 99
    assert shared['nested'][0]['value'] == 7
    assert first['Query']['copy_b']['nested'][0]['value'] == 7
    assert second['Query']['copy_a']['nested'][0]['value'] == 7
    assert second['Query']['copy_a']['nested'][0]['$ref'].startswith(schema_v2.BASE)


def test_ordinary_builder_mutation_does_not_change_next_build_or_legacy():
    legacy = deepcopy(schema_v1.definitions())
    first = schema_v2.definitions()
    expected = deepcopy(schema_v2.definitions())
    first[0]['Query']['properties'].clear()
    first[1]['event']['oneOf'].pop()
    assert schema_v2.definitions() == expected
    assert schema_v1.definitions() == legacy


def test_unknown_non_json_metadata_still_fails_closed_at_compilation(monkeypatch):
    source = schema_v1.definitions()
    source[0]['Query']['unsupported_metadata'] = object()
    monkeypatch.setattr(schema_v2.old, 'definitions', lambda: source)
    rewritten = schema_v2.definitions()
    with pytest.raises(TypeError, match='exact JSON types'):
        _compile_schema(rewritten[0])
