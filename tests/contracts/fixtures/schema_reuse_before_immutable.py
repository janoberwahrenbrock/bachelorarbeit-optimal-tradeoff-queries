"""Private bounded successes within one native document validation call.

There is no filesystem/artifact cache. Only static Planning/PlanSummary refs
from this validator construction are eligible, with the exact JSON value and
the actual type-checker, format-checker and registry context in the key.
"""
from __future__ import annotations

from contextvars import ContextVar
from copy import deepcopy
import json
import math


_CURRENT = ContextVar('otqa_document_validation', default=None)
_MAX_ENTRIES = 64
_MAX_KEY_BYTES = 512 * 1024
_REF_NAMES = ('Planning', 'PlanSummary')
_EVENTS = frozenset(('planning_attempt_completed', 'planning_resolved', 'query_completed'))
_SCOPE_KEYS = frozenset(('$id', '$schema', '$anchor', '$dynamicAnchor', '$dynamicRef', '$recursiveRef', 'format'))


def _plain_json(value, active=None):
    """No coercion of tuple, scalar/container subclasses, or nonfinite values."""
    kind = type(value)
    if value is None or kind in (str, bool, int):
        return True
    if kind is float:
        return math.isfinite(value)
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
            return all(type(k) is str and _plain_json(v, active) for k, v in value.items())
        return all(_plain_json(v, active) for v in value)
    finally:
        active.remove(identity)


def _exact_json(value, limit=_MAX_KEY_BYTES):
    try:
        if not _plain_json(value):
            return None
        # Plain exact types retain 1 vs 1.0, true vs 1, and -0.0 vs +0.0.
        raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
            separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (ValueError, TypeError, OverflowError, UnicodeError, RecursionError):
        return None
    return raw if len(raw) <= limit else None


def _same_schema(value, expected):
    """Exact plain-type equality against a private construction-time snapshot."""
    if type(value) is not type(expected):
        return False
    if type(value) is dict:
        return value.keys() == expected.keys() and all(
            type(k) is str and _same_schema(v, expected[k]) for k, v in value.items())
    if type(value) is list:
        return len(value) == len(expected) and all(_same_schema(a, b) for a, b in zip(value, expected))
    if type(value) is float:
        return math.isfinite(value) and value.hex() == expected.hex()
    return (value is None or type(value) in (str, bool, int)) and value == expected


class _ValidationCall:
    def __init__(self, namespace, allowed_bases):
        self.namespace = namespace
        self.allowed_bases = allowed_bases
        self.successes = set()
        self.key_bytes = 0

    def remember(self, key):
        size = len(key[-1]) + len(key[1])
        if key in self.successes:
            return
        if len(self.successes) < _MAX_ENTRIES and self.key_bytes + size <= _MAX_KEY_BYTES:
            self.successes.add(key)
            self.key_bytes += size


class ReferenceReuse:
    """One factory's trusted static schemas; carries no validated user data."""
    def __init__(self, original_ref):
        self.original_ref = original_ref
        self.namespace = object()
        self.targets = {}
        self.roots = {}
        self.allowed_bases = set()
        self.families = {}

    def register_family(self, base, definitions):
        self.allowed_bases.add(base + 'common')
        for name in _REF_NAMES:
            self.targets[base + 'common#/$defs/' + name] = definitions[name]
        # Include every transitive static definition, not only the two roots.
        pending, names, safe = list(_REF_NAMES), set(), True
        prefix = base + 'common#/$defs/'
        def inspect(value):
            nonlocal safe
            if type(value) is dict:
                if _SCOPE_KEYS.intersection(value):
                    safe = False
                ref = value.get('$ref')
                if ref is not None:
                    if type(ref) is not str or not ref.startswith(prefix) or ref[len(prefix):] not in definitions:
                        safe = False
                    else:
                        pending.append(ref[len(prefix):])
                for child in value.values():
                    inspect(child)
            elif type(value) is list:
                for child in value:
                    inspect(child)
        while pending:
            name = pending.pop()
            if name not in names:
                names.add(name)
                inspect(definitions[name])
        snapshot = {name: deepcopy(definitions[name]) for name in sorted(names)}
        self.families[base + 'common'] = (definitions, tuple(sorted(names)), snapshot if safe else None)

    def register_root(self, kind, validator):
        if kind in ('event', 'result'):
            schema = validator.schema
            self.roots[id(schema)] = (schema, deepcopy(schema), validator.TYPE_CHECKER,
                validator.format_checker, dict(validator.format_checker.checkers), validator._resolver)
            self.allowed_bases.add(schema['$id'])

    def begin(self, kind, validator, document):
        event_type = document.get('event_type') if type(document) is dict else None
        if (type(document) is not dict or document.get('schema_version') != 2
                or kind not in ('event', 'result')
                or kind == 'event' and (type(event_type) is not str or event_type not in _EVENTS)):
            return _CURRENT.set(None)
        expected = self.roots.get(id(validator.schema))
        # Unknown/evolved/mutated schemas never inherit a caller's context.
        enabled = (expected is not None and expected[0] is validator.schema
            and validator.TYPE_CHECKER is expected[2] and validator.format_checker is expected[3]
            and validator._resolver is expected[5] and validator._ref_resolver is None
            and validator.format_checker.checkers == expected[4]
            and all(getattr(check, '__module__', None) == 'jsonschema._format' for check, _ in expected[4].values())
            and _same_schema(validator.schema, expected[1]))
        family = self.families.get('urn:otqa:v2:common')
        if enabled:
            definitions, names, snapshot = family
            enabled = snapshot is not None and _same_schema({name: definitions.get(name) for name in names}, snapshot)
        return _CURRENT.set(_ValidationCall(self.namespace, frozenset(self.allowed_bases)) if enabled else None)

    def reference(self, validator, ref, instance, schema):
        context = _CURRENT.get()
        if (context is None or context.namespace is not self.namespace
                or type(ref) is not str or ref not in self.targets
                or type(schema) is not dict or set(schema) != {'$ref'}
                or validator._ref_resolver is not None
                or getattr(validator._resolver, '_base_uri', None) not in context.allowed_bases):
            yield from self.original_ref(validator, ref, instance, schema)
            return
        # An altered resolver/resource is not the trusted common definition.
        try:
            resolved = validator._resolver.lookup(ref)
        except Exception:
            yield from self.original_ref(validator, ref, instance, schema)
            return
        if resolved.contents is not self.targets[ref]:
            yield from self.original_ref(validator, ref, instance, schema)
            return
        raw = _exact_json(instance)
        if raw is None:
            yield from self.original_ref(validator, ref, instance, schema)
            return
        key = (self.namespace, ref, id(validator.TYPE_CHECKER), id(validator.format_checker),
            id(resolved.resolver._registry), raw)
        if key in context.successes:
            return
        valid = True
        for error in self.original_ref(validator, ref, instance, schema):
            valid = False
            # Yield immediately: do not reorder or eagerly consume failures.
            yield error
        if valid:
            context.remember(key)


def end_call(token):
    _CURRENT.reset(token)


def begin_call(kind, validator, document):
    owner = getattr(validator, '_otqa_reference_reuse', None)
    return _CURRENT.set(None) if owner is None else owner.begin(kind, validator, document)
