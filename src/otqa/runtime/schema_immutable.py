"""Private, deeply read-only compiled copies of native JSON-schema metadata.

Raw builders and exported JSON resources remain ordinary JSON. A mapping proxy
owns a newly created backing dictionary; no mutable builder alias is retained.
Builtin tuple storage is immutable without a heap-type class-assignment escape.
Known-native enum diagnostics retain list spelling through the full original
enum handler, independently of this internal representation.
"""
from __future__ import annotations

import math
from types import MappingProxyType


_SchemaSequence = tuple


def _compile_schema(value, active=None):
    kind = type(value)
    if value is None or kind in (bool, str, int):
        return value
    if kind is float and math.isfinite(value):
        return value
    if kind not in (dict, list):
        raise TypeError('Native schema metadata must contain exact JSON types')
    active = set() if active is None else active
    identity = id(value)
    if identity in active:
        raise ValueError('Native schema metadata contains a cycle')
    active.add(identity)
    try:
        if kind is dict:
            if any(type(key) is not str for key in value):
                raise TypeError('Native schema metadata keys must be exact strings')
            return MappingProxyType({key: _compile_schema(child, active) for key, child in value.items()})
        return _SchemaSequence(_compile_schema(child, active) for child in value)
    finally:
        active.remove(identity)


def _thaw_schema(value):
    """Fresh construction-only view of trusted immutable schema metadata."""
    if type(value) is MappingProxyType:
        return {key: _thaw_schema(child) for key, child in value.items()}
    if type(value) is tuple:
        return [_thaw_schema(child) for child in value]
    if value is None or type(value) in (bool, str, int, float):
        return value
    raise TypeError('Unknown compiled schema metadata type')
