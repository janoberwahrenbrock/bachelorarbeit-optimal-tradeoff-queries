"""Offline schemas addressed by document kind and immutable contract version."""
from __future__ import annotations
from functools import lru_cache
from types import MappingProxyType
from typing import Any
from . import schema_v1, schema_v2
from .codec import DocumentError
from .schema_reuse import ReferenceReuse, begin_call, end_call
from .schema_immutable import _compile_schema, _SchemaSequence

# Legacy construction API remains available to readers of historical artifacts.
BASE, DIALECT = schema_v1.BASE, schema_v1.DIALECT
definitions = schema_v1.definitions
VERSION = schema_v1.VERSION


def latest_version(kind: str) -> int:
    return 2 if kind in schema_v2.KINDS else 1


def versioned_definitions(version: int):
    if version == 1:
        return schema_v1.definitions()
    if version == 2:
        return schema_v2.definitions()
    raise DocumentError(f'Unsupported schema version: {version}')


@lru_cache(maxsize=1)
def all_validators():
    from jsonschema import Draft202012Validator, FormatChecker, validators
    from referencing import Registry, Resource
    checker = Draft202012Validator.TYPE_CHECKER.redefine('integer', lambda checker, v: type(v) is int)
    checker = checker.redefine('number', lambda checker, v: type(v) in (int, float) and schema_v1._finite(v))
    reuse = ReferenceReuse(Draft202012Validator.VALIDATORS['$ref'], Draft202012Validator.VALIDATORS['enum'])
    strict = validators.extend(Draft202012Validator, {'$ref': reuse.reference, 'enum': reuse.enumeration}, type_checker=checker)
    registry = Registry()
    families = {}
    for version, module in ((1, schema_v1), (2, schema_v2)):
        defs, docs = module.definitions()
        if version == 1:
            from .schema_v2 import continuation_schema
            docs['continuation'] = continuation_schema()
        families[version] = docs
        common = _compile_schema({'$schema': DIALECT, '$id': module.BASE + 'common', '$defs': defs})
        reuse.register_metadata(common)
        reuse.register_family(module.BASE, common['$defs'])
        registry = registry.with_resource(module.BASE + 'common', Resource.from_contents(common))
    result = {(kind, version): strict(_compile_schema({'$schema': DIALECT, '$id': f'urn:otqa:v{version}:' + kind, **doc}),
            registry=registry, format_checker=FormatChecker())
            for version, docs in families.items() for kind, doc in docs.items()}
    for (kind, _), validator in result.items():
        reuse.register_metadata(validator.schema)
        reuse.register_root(kind, validator)
    strict._otqa_reference_reuse = reuse
    return result


def registry_and_validators(version=1):
    return {kind: v for (kind, ver), v in all_validators().items() if ver == version}



@lru_cache(maxsize=2)
def _event_validators(version: int):
    """Compile the unique event discriminator without weakening oneOf admission.

    Only the known metadata-only envelope is eligible. A different schema shape
    or nonunique discriminator falls back to the full validator. Evolve without
    a dialect declaration retains our strict integer/finite-number type checker.
    """
    validator = all_validators()['event', version]
    schema = validator.schema
    if type(schema) is MappingProxyType:
        owner = getattr(validator, '_otqa_reference_reuse', None)
        known = owner.roots.get(id(schema)) if owner is not None else None
        if known is None or known[0] is not schema:
            return {}
    if not isinstance(schema, dict) and type(schema) is not MappingProxyType:
        return {}
    if set(schema) != {'$schema', '$id', 'oneOf'}:
        return {}
    if not isinstance(schema['oneOf'], list) and type(schema['oneOf']) is not _SchemaSequence:
        return {}
    result = {}
    for variant in schema['oneOf']:
        if (not isinstance(variant, dict) and type(variant) is not MappingProxyType) or any(
            key in variant for key in ('$id', '$schema', '$anchor', '$dynamicAnchor')
        ):
            return {}
        properties = variant.get('properties')
        if ((not isinstance(properties, dict) and type(properties) is not MappingProxyType)
                or (not isinstance(properties.get('event_type'), dict)
                    and type(properties.get('event_type')) is not MappingProxyType)):
            return {}
        tag = properties['event_type'].get('const')
        if type(tag) is not str or tag in result:
            return {}
        result[tag] = validator.evolve(schema=variant)
    return result


def validate(kind: str, document: Any) -> Any:
    if not isinstance(document, dict) or type(document.get('schema_version')) is not int:
        raise DocumentError(f'{kind} has no integer schema_version')
    version = document['schema_version']
    try:
        validator = all_validators()[kind, version]
    except KeyError as exc:
        raise DocumentError(f'Unknown native document kind/version: {kind}/{version}') from exc
    token = begin_call(kind, validator, document)
    try:
        if kind == 'event' and type(document) is dict and type(document.get('event_type')) is str:
            selected = _event_validators(version).get(document['event_type'])
            if selected is not None and selected.is_valid(document):
                return document
        # Invalid data retains the full validator's established error ordering.
        errors = sorted(validator.iter_errors(document), key=lambda e: str(list(e.path)))
        if errors:
            first = errors[0]
            raise DocumentError(f"{kind} v{version} at /{'/'.join(map(str, first.path))}: {first.message}")
        return document
    finally:
        end_call(token)


def write_schema_resources(directory):
    from pathlib import Path
    from .codec import encode
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    resources = {}
    for version, module in ((1, schema_v1), (2, schema_v2)):
        defs, docs = module.definitions()
        if version == 1:
            from .schema_v2 import continuation_schema
            docs['continuation'] = continuation_schema()
        suffix = '' if version == 1 else '.v2'
        resources['common' + suffix] = {'$schema': DIALECT, '$id': module.BASE + 'common', '$defs': defs}
        resources.update({kind + suffix: {'$schema': DIALECT, '$id': module.BASE + kind, **doc} for kind, doc in docs.items()})
    for kind, doc in resources.items():
        (root / f'{kind}.schema.json').write_bytes(encode(doc))
    return tuple(resources)
