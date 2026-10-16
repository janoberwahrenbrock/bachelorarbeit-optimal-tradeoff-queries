"""Offline qualification fully checks the actual immutable schemas as JSON."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, SchemaError
import pytest

import otqa
from otqa.runtime import schema
from otqa.runtime.schema_immutable import _compile_schema, _thaw_schema
from tools.qualification.qualify import Controls


def offline_schemas():
    # This installation control needs no native run, source claim, or Controls
    # constructor side effects; it checks the currently loaded package schemas.
    return object.__new__(Controls).installation('offline_schemas')


def test_all_actual_compiled_roots_and_raw_resources_pass_full_metaschema():
    validators = schema.all_validators()
    resources = {document['$id']: document for path in
        (Path(otqa.__file__).parent / 'schemas').glob('*.schema.json')
        for document in [json.loads(path.read_bytes())]}
    assert len(validators) == 38
    assert len(resources) == 40
    for validator in validators.values():
        view = _thaw_schema(validator.schema)
        assert type(view) is dict
        assert view == resources[view['$id']]
        validator.check_schema(view)
    for raw in resources.values():
        Draft202012Validator.check_schema(raw)
    assert offline_schemas() == {
        'document_validators': 38, 'schema_resources': 40, 'versions': [1, 2]}


@pytest.mark.parametrize('invalid', [
    {'type': 'invalid-native-type'},
    {'required': 'not-an-array'},
    {'properties': {'nested': {'minimum': 'not-a-number'}}},
    {'oneOf': []},
])
def test_malformed_actual_compiled_root_still_fails_full_schema_check(monkeypatch, invalid):
    validators = schema.all_validators()
    actual = validators['config', 2]
    view = _thaw_schema(actual.schema)
    view.update(invalid)
    with pytest.raises(SchemaError) as expected:
        actual.check_schema(view)
    broken = type(actual)(_compile_schema(view), registry=actual._registry,
        format_checker=actual.format_checker)
    changed = {**validators, ('config', 2): broken}
    monkeypatch.setattr(schema, 'all_validators', lambda: changed)
    with pytest.raises(SchemaError) as observed:
        offline_schemas()
    assert observed.value.message == expected.value.message
    assert list(observed.value.path) == list(expected.value.path)


def test_json_view_is_fresh_and_preserves_all_nested_constraints():
    actual = schema.all_validators()['event', 2]
    first = _thaw_schema(actual.schema)
    second = _thaw_schema(actual.schema)
    assert first == second
    assert first is not second and first['oneOf'] is not second['oneOf']
    first['oneOf'][0]['properties']['sequence']['minimum'] = 'broken'
    with pytest.raises(SchemaError):
        actual.check_schema(first)
    assert second == _thaw_schema(actual.schema)
    actual.check_schema(second)
