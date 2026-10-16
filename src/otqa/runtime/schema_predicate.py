"""Positive certificates for a closed, format-free native JSON-schema subset.

False always means use the original validator, never reject the document here.
The entire input first enters a plain finite-JSON domain. Within that domain
each compiled boolean is equivalent, so oneOf cannot mistake unknown for false.
"""
from __future__ import annotations

from copy import deepcopy
import math
import re
import sys


_KEYWORDS = frozenset(('$ref', 'type', 'properties', 'required', 'additionalProperties',
    'items', 'minItems', 'minimum', 'maximum', 'exclusiveMinimum', 'anyOf', 'oneOf',
    'enum', 'const', 'pattern', 'uniqueItems'))
_TYPES = frozenset(('object', 'array', 'string', 'integer', 'number', 'boolean', 'null'))
_MAX_CERTIFICATE_DEPTH = 24
_DEFINITION_NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]*\Z')


def _finite_number(value):
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _plain_native(value, active=None, depth=0):
    if depth > _MAX_CERTIFICATE_DEPTH:
        return False
    kind = type(value)
    if value is None or kind in (str, bool):
        return True
    if kind in (int, float):
        return _finite_number(value)
    if kind not in (dict, list):
        return False
    if active is None:
        active = set()
    identity = id(value)
    if identity in active:
        return False
    active.add(identity)
    try:
        if kind is dict:
            # Check every key before ANY compiled property lookup/equality.
            if any(type(key) is not str for key in value):
                return False
            return all(_plain_native(child, active, depth + 1) for child in value.values())
        return all(_plain_native(child, active, depth + 1) for child in value)
    finally:
        active.remove(identity)


def _equal(left, right):
    a, b = type(left), type(right)
    if a in (int, float) and b in (int, float):
        return left == right
    if a is not b:
        return False
    if a is list:
        return len(left) == len(right) and all(_equal(x, y) for x, y in zip(left, right))
    if a is dict:
        return left.keys() == right.keys() and all(_equal(v, right[k]) for k, v in left.items())
    return left == right


class _Compiler:
    def __init__(self, base, definitions):
        self.prefix = base + 'common#/$defs/'
        self.definitions = definitions
        self.definitions_compiled = {}
        self.failed = False

    def definition(self, name):
        # Literal lookup is valid only for canonical native pointer segments.
        # Escaped URI/JSON-pointer names are deliberately left to jsonschema.
        if type(name) is not str or _DEFINITION_NAME.fullmatch(name) is None:
            self.failed = True
            return None
        if name in self.definitions_compiled:
            return self.definitions_compiled[name][0]
        if name not in self.definitions:
            self.failed = True
            return None
        slot = [None]
        def recursive(value):
            return slot[0](value)
        self.definitions_compiled[name] = recursive, slot
        compiled = self.node(self.definitions[name])
        if compiled is None:
            self.failed = True
        slot[0] = compiled
        return recursive

    def node(self, schema):
        if type(schema) is bool:
            return lambda value: schema
        if (type(schema) is not dict or any(type(k) is not str for k in schema)
                or not set(schema) <= _KEYWORDS):
            return None
        checks = []
        for keyword, argument in schema.items():
            check = self.keyword(keyword, argument, schema)
            if check is None:
                return None
            checks.append(check)
        checks = tuple(checks)
        return lambda value: all(check(value) for check in checks)

    def keyword(self, keyword, argument, schema):
        if keyword == '$ref':
            if type(argument) is not str or not argument.startswith(self.prefix):
                return None
            name = argument[len(self.prefix):]
            if _DEFINITION_NAME.fullmatch(name) is None:
                return None
            return self.definition(name)
        if keyword == 'type':
            if type(argument) is not str or argument not in _TYPES:
                return None
            if argument == 'number':
                return lambda value: type(value) in (int, float)
            expected = {'object': dict, 'array': list, 'string': str, 'integer': int,
                'boolean': bool, 'null': type(None)}[argument]
            return lambda value: type(value) is expected
        if keyword in ('minimum', 'maximum', 'exclusiveMinimum'):
            if not _finite_number(argument):
                return None
            if keyword == 'minimum':
                return lambda value: type(value) not in (int, float) or value >= argument
            if keyword == 'maximum':
                return lambda value: type(value) not in (int, float) or value <= argument
            return lambda value: type(value) not in (int, float) or value > argument
        if keyword == 'properties':
            if type(argument) is not dict or any(type(k) is not str for k in argument):
                return None
            fields = tuple((key, self.node(child)) for key, child in argument.items())
            if any(check is None for _, check in fields):
                return None
            return lambda value: type(value) is not dict or all(
                key not in value or check(value[key]) for key, check in fields)
        if keyword == 'required':
            if type(argument) is not list or any(type(k) is not str for k in argument):
                return None
            names = tuple(argument)
            return lambda value: type(value) is not dict or all(key in value for key in names)
        if keyword == 'additionalProperties':
            properties = schema.get('properties', {})
            if type(properties) is not dict or any(type(k) is not str for k in properties):
                return None
            names = frozenset(properties)
            if type(argument) is bool:
                if argument:
                    return lambda value: True
                return lambda value: type(value) is not dict or all(key in names for key in value)
            child = self.node(argument)
            if child is None:
                return None
            return lambda value: type(value) is not dict or all(
                key in names or child(item) for key, item in value.items())
        if keyword == 'items':
            child = self.node(argument)
            if child is None:
                return None
            return lambda value: type(value) is not list or all(child(item) for item in value)
        if keyword == 'minItems':
            if type(argument) is not int or argument < 0:
                return None
            return lambda value: type(value) is not list or len(value) >= argument
        if keyword == 'uniqueItems':
            if type(argument) is not bool:
                return None
            if not argument:
                return lambda value: True
            return lambda value: type(value) is not list or all(
                not _equal(item, earlier) for index, item in enumerate(value)
                for earlier in value[:index])
        if keyword in ('anyOf', 'oneOf'):
            if type(argument) is not list or not argument:
                return None
            alternatives = tuple(self.node(child) for child in argument)
            if any(child is None for child in alternatives):
                return None
            if keyword == 'anyOf':
                return lambda value: any(child(value) for child in alternatives)
            return lambda value: sum(bool(child(value)) for child in alternatives) == 1
        if keyword == 'enum':
            if type(argument) is not list or not argument or not _plain_native(argument):
                return None
            values = deepcopy(argument)
            return lambda value: any(_equal(value, choice) for choice in values)
        if keyword == 'const':
            if not _plain_native(argument):
                return None
            expected = deepcopy(argument)
            return lambda value: _equal(value, expected)
        if keyword == 'pattern':
            if type(argument) is not str:
                return None
            try:
                pattern = re.compile(argument)
            except re.error:
                return None
            return lambda value: type(value) is not str or pattern.search(value) is not None
        return None


def compile_reference(base, definitions, name):
    """Return a positive certifier, or None unless the complete closure compiles."""
    compiler = _Compiler(base, definitions)
    try:
        compiled = compiler.definition(name)
    except (TypeError, ValueError, RecursionError):
        return None
    if compiled is None or compiler.failed:
        return None
    def certify(value):
        try:
            return sys.getrecursionlimit() >= 1000 and _plain_native(value) and compiled(value)
        except (TypeError, ValueError, OverflowError, RecursionError):
            return False
    return certify
