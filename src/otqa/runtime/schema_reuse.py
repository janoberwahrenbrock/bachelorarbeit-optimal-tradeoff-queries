"""Immutable schema metadata and positive certificates; no user-data cache.

Every call has fresh authorization only. No instance, serialized key, successful
validation or cross-document trust is retained. Negative certificates always
use the complete original jsonschema reference validator.
"""
from __future__ import annotations

from contextvars import ContextVar
from types import FunctionType, MappingProxyType, MethodType

from . import schema_v1
from .schema_immutable import _SchemaSequence, _thaw_schema
from .schema_predicate import _KEYWORDS as _PREDICATE_KEYWORDS, compile_reference, compile_references

_CURRENT = ContextVar('otqa_document_validation', default=None)
_PREDICATE_NAMES = ('Planning', 'PlanSummary', 'ProgressEvidence', 'ExecutionCursor',
    'HorizonSelectionEvidence', 'PlanningAttempt', 'PlanningCycle')
_EVENTS = frozenset(('planning_attempt_completed', 'planning_resolved', 'query_completed'))
_SCOPE_KEYS = frozenset(('$id', '$schema', '$anchor', '$dynamicAnchor', '$dynamicRef', '$recursiveRef', 'format'))


def _native_function(function, module, name):
    """Ordinary pre/post-factory callback overrides are not schema authority."""
    return (type(function) is FunctionType and function.__module__ == module.__name__
        and function.__name__ == name and function.__globals__ is vars(module)
        and function.__code__.co_filename == module.__file__)


def _native_method(actual, expected):
    return (type(actual) is FunctionType and actual.__code__ is expected.__code__
        and actual.__globals__ is expected.__globals__)


class _ValidationCall:
    """Authorization only; no validated instance or success key is retained."""
    def __init__(self, namespace, allowed_bases, *, validator=None):
        self.namespace = namespace
        self.allowed_bases = allowed_bases
        self.active = True
        self.validator_type = type(validator) if validator is not None else None
        self.type_checker = validator.TYPE_CHECKER if validator is not None else None
        self.format_checker = validator.format_checker if validator is not None else None


class ReferenceReuse:
    """One factory's trusted static schemas; carries no validated user data."""
    def __init__(self, original_ref, original_enum=None):
        # jsonschema is already imported by the existing validator factory.
        from jsonschema import _keywords, _types, Draft202012Validator, validators
        self.original_ref = original_ref
        self.original_enum = original_enum
        self.enum_schemas = {}
        self.native_keywords = tuple((name, getattr(_keywords, name))
            for name in sorted(_PREDICATE_KEYWORDS - {'$ref'}))
        self.native_finite = schema_v1._finite
        self.native_methods = tuple((name, getattr(Draft202012Validator, name))
            for name in ('_validate_reference', 'is_type', 'descend', 'evolve'))
        self.native_ref = _keywords.ref
        self.native_type_checks = tuple((name, getattr(_types, function)) for name, function in (
            ('array', 'is_array'), ('object', 'is_object'), ('string', 'is_string'),
            ('boolean', 'is_bool'), ('null', 'is_null')))
        self.native_semantics_supported = (
            _native_function(self.native_finite, schema_v1, '_finite')
            and _native_function(self.native_ref, _keywords, 'ref')
            and all(_native_function(function, _keywords, name) for name, function in self.native_keywords)
            and all(_native_function(function, _types, function.__name__)
                for _, function in self.native_type_checks)
            and all(_native_function(function, validators, name) for name, function in self.native_methods))
        self.namespace = object()
        self.targets = {}
        self.roots = {}
        self.allowed_bases = set()
        self.families = {}
        self.predicates = {}

    def register_metadata(self, schema):
        """Retain immutable native enum node identities, never mutable aliases."""
        if type(schema) is MappingProxyType:
            if 'enum' in schema and type(schema['enum']) is tuple:
                self.enum_schemas[id(schema)] = schema
            for child in schema.values():
                self.register_metadata(child)
        elif type(schema) is tuple:
            for child in schema:
                self.register_metadata(child)

    def enumeration(self, validator, enums, instance, schema):
        # Full original admission and error ordering. Only the known immutable
        # internal representation receives its historical list diagnostic view.
        if self.enum_schemas.get(id(schema)) is schema and type(enums) is tuple:
            enums = list(enums)
        yield from self.original_enum(validator, enums, instance, schema)

    def register_family(self, base, definitions):
        if type(definitions) is not MappingProxyType:
            self.families[base + 'common'] = False
            return
        self.allowed_bases.add(base + 'common')
        # Include every transitive static definition, not only the two roots.
        selected = tuple(name for name in _PREDICATE_NAMES if name in definitions)
        pending, names, safe = list(selected), set(), True
        prefix = base + 'common#/$defs/'
        def inspect(value):
            nonlocal safe
            if type(value) is MappingProxyType:
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
            elif type(value) is _SchemaSequence:
                for child in value:
                    inspect(child)
        while pending:
            name = pending.pop()
            if name not in names:
                names.add(name)
                inspect(definitions[name])
        self.families[base + 'common'] = safe

        if safe and base == 'urn:otqa:v2:':
            plain = _thaw_schema(definitions)
            compiled = compile_references(base, plain, selected)
            for name in selected:
                ref = prefix + name
                self.targets[ref] = definitions[name]
                self.predicates[ref] = (compiled[name] if compiled is not None
                    else compile_reference(base, plain, name))

    def register_root(self, kind, validator):
        if kind in ('event', 'result') and type(validator.schema) is MappingProxyType:
            schema = validator.schema
            self.roots[id(schema)] = (schema, validator.TYPE_CHECKER,
                validator.format_checker, dict(validator.format_checker.checkers), validator._resolver,
                type(validator))
            self.allowed_bases.add(schema['$id'])

    def _native_handlers(self, validator):
        table = validator.VALIDATORS
        if type(table) is not dict or any(type(name) is not str for name in table):
            return False
        for name, function in self.native_keywords:
            actual = table.get(name)
            if name == 'enum':
                if not (type(actual) is MethodType and actual.__self__ is self
                        and actual.__func__ is ReferenceReuse.enumeration
                        and self.original_enum is function):
                    return False
            elif actual is not function:
                return False
        return True

    def begin(self, kind, validator, document):
        event_type = document.get('event_type') if type(document) is dict else None
        if (type(document) is not dict or document.get('schema_version') != 2
                or kind not in ('event', 'result')
                or kind == 'event' and (type(event_type) is not str or event_type not in _EVENTS)):
            return _CURRENT.set(None)
        expected = self.roots.get(id(validator.schema))
        # Compiled roots and all referenced metadata are deeply immutable.
        # Unknown/evolved schemas never inherit a caller's context.
        enabled = (expected is not None and expected[0] is validator.schema
            and type(validator) is expected[5]
            and validator.TYPE_CHECKER is expected[1] and validator.format_checker is expected[2]
            and validator._resolver is expected[4] and validator._ref_resolver is None
            and validator.format_checker.checkers == expected[3]
            and all(getattr(check, '__module__', None) == 'jsonschema._format' for check, _ in expected[3].values())
            and self.families.get('urn:otqa:v2:common') is True
            and self.native_semantics_supported and self.original_ref is self.native_ref
            and schema_v1._finite is self.native_finite and self._native_handlers(validator)
            and all(validator.TYPE_CHECKER._type_checkers.get(name) is function
                for name, function in self.native_type_checks)
            and all(_native_method(vars(type(validator)).get(name), function)
                for name, function in self.native_methods))
        return _CURRENT.set(_ValidationCall(self.namespace, frozenset(self.allowed_bases),
            validator=validator) if enabled else None)

    def reference(self, validator, ref, instance, schema):
        context = _CURRENT.get()
        if (context is None or context.namespace is not self.namespace
                or not context.active or context.validator_type is not type(validator)
                or context.type_checker is not validator.TYPE_CHECKER
                or context.format_checker is not validator.format_checker
                or type(ref) is not str or ref not in self.predicates
                or type(schema) is not MappingProxyType or set(schema) != {'$ref'}
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
        predicate = self.predicates[ref]
        if predicate is not None and predicate(instance):
            return
        yield from self.original_ref(validator, ref, instance, schema)


def end_call(token):
    context = _CURRENT.get()
    if type(context) is _ValidationCall:
        context.active = False
    _CURRENT.reset(token)


def begin_call(kind, validator, document):
    owner = getattr(validator, '_otqa_reference_reuse', None)
    return _CURRENT.set(None) if owner is None else owner.begin(kind, validator, document)
