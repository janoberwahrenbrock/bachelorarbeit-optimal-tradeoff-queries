"""Independent schema-resource oracle and adversarial positive-proof review."""
from copy import deepcopy
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, validators
from referencing import Registry, Resource
import pytest

from otqa.runtime import schema, schema_predicate
from otqa.runtime.codec import DocumentError


BASE = 'urn:otqa:v2:'
PREFIX = BASE + 'common#/$defs/'
RESOURCES = Path(__file__).resolve().parents[2] / 'src/otqa/schemas'
COMMON = json.loads((RESOURCES / 'common.v2.schema.json').read_bytes())
DEFINITIONS = COMMON['$defs']


def finite(value):
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


CHECKER = Draft202012Validator.TYPE_CHECKER.redefine('integer', lambda _, v: type(v) is int)
CHECKER = CHECKER.redefine('number', lambda _, v: type(v) in (int, float) and finite(v))
ORACLE = validators.extend(Draft202012Validator, type_checker=CHECKER)


def original(node, definitions=None):
    resource = {**COMMON, '$defs': DEFINITIONS if definitions is None else definitions}
    registry = Registry().with_resource(BASE + 'common', Resource.from_contents(resource))
    return ORACLE(node, registry=registry, format_checker=FormatChecker())


def samples():
    query = {'goal_index_a': 0, 'goal_index_b': 1, 'value': .75}
    score = {'kind': 'fixed', 'expected_terminal_candidates': 2., 'expected_terminal_loss': 2.,
             'expected_queries': 1.5, 'lexicographic_expected_values': [2.]}
    summary = {'query': query, 'horizon': 2, 'score': score,
               'answer_probabilities': {'<': .25, '=': 0., '>': .75}}
    tree = {'node_id': 'root', 'candidate_count': 3, 'stop_reason': None, 'maximum_volume_share': .5,
            'query': query, 'expected_terminal_candidates': 2., 'expected_terminal_loss': 2.,
            'expected_queries': 1.5, 'branches': []}
    plan = {'selected': summary, 'horizons': [{'horizon': 2, 'status': 'available', 'plan': summary}],
            'planning_stop_aware': False, 'plan_tree': tree}
    progress = {'basis': 'candidate_count', 'starting_value': 3., 'expected_terminal_value': 2.,
                'expected_progress': 1., 'threshold': .001, 'comparison': 'strict_greater', 'admissible': True}
    horizon = {'horizon': 2, 'generated_query_count': 1, 'evaluated_query_count': 1, 'outcome': 'available',
               'selected_plan': plan, 'selected_progress': progress, 'best_progress_witness': plan,
               'best_progress': progress}
    attempt = {'requested_depth': 2, 'evaluated_horizons': [2], 'outcome': 'available',
               'selected_plan': plan, 'selected_progress': progress, 'best_progress_witness': plan,
               'horizon_evidence': [horizon]}
    cursor = {'answered_total': 0, 'remaining_depth': 2}
    cycle = {'cursor_before': cursor, 'attempts': [attempt], 'selected_plan': plan, 'outcome': 'available',
             'restart_reason': None, 'proposed_cursor_after_answer': {'answered_total': 1, 'remaining_depth': 1}}
    return {'Planning': plan, 'PlanSummary': summary, 'ProgressEvidence': progress, 'ExecutionCursor': cursor,
            'HorizonSelectionEvidence': horizon, 'PlanningAttempt': attempt, 'PlanningCycle': cycle}


def event():
    return {'schema_version': 2, 'run_id': '00000000-0000-4000-8000-000000000001',
            'attempt_id': 'attempt0001', 'sequence': 1, 'occurred_at_utc': '2026-10-16T00:00:00Z',
            'monotonic_ns': 1, 'event_type': 'planning_attempt_completed', 'query_id': None, 'numeric_hex': {},
            'payload': {'state_before_index': 0, 'execution_cursor': {'answered_total': 0, 'remaining_depth': 2},
                        'attempt_index': 1, 'attempt': deepcopy(samples()['PlanningAttempt'])}}


@pytest.mark.parametrize('name', tuple(samples()))
def test_all_seven_targets_certify_independent_native_samples_and_mutations(name):
    predicate = schema_predicate.compile_reference(BASE, DEFINITIONS, name)
    oracle = original({'$ref': PREFIX + name})
    valid = deepcopy(samples()[name])
    assert oracle.is_valid(valid) and predicate is not None and predicate(valid)
    changes = []
    for key in valid:
        removed = deepcopy(valid)
        del removed[key]
        changes.append(removed)
        for wrong in (None, True, -1, 0., '', [], {}, math.nan, math.inf, 10**400):
            replaced = deepcopy(valid)
            replaced[key] = wrong
            changes.append(replaced)
    changes.append({**deepcopy(valid), 'unexpected': True})
    for value in changes:
        positive = predicate(value)
        assert not positive or oracle.is_valid(value), (name, value)


@pytest.mark.parametrize('bad_tail', ['A~1B', 'A%2FB', 'A/B', 'A#B'])
def test_escaped_or_noncanonical_reference_names_decline_instead_of_resolving_wrong_definition(bad_tail):
    definitions = {'Planning': {'$ref': PREFIX + bad_tail}, bad_tail: {'const': 1}, 'A/B': {'const': 2}}
    assert schema_predicate.compile_reference(BASE, definitions, 'Planning') is None


@pytest.mark.parametrize('node', [
    {'type': 'number', 'not': {'const': 1}},
    {'properties': {'x': {'type': 'number'}}, 'patternProperties': {'^x': {'maximum': 0}}},
    {'type': 'array', 'maxItems': 1},
    {'type': 'string', 'minLength': 1},
    {'type': 'number', 'multipleOf': .5},
    {'$ref': PREFIX + 'Other', 'unevaluatedProperties': False},
])
def test_no_unknown_keyword_is_silently_omitted(node):
    definitions = {'Planning': node, 'Other': {}}
    assert schema_predicate.compile_reference(BASE, definitions, 'Planning') is None


@pytest.mark.parametrize('node', [
    {'oneOf': [{'uniqueItems': True}, {'type': 'array'}]},
    {'oneOf': [{'type': 'integer'}, {'type': 'number'}]},
    {'oneOf': [{'const': {'x': True}}, {'const': {'x': 1}}]},
    {'enum': [True, 1., [True], {'x': [False]}]},
    {'type': 'object', 'properties': {'x': {'minimum': 0}}, 'additionalProperties': {'maximum': 2}},
    {'type': 'number', 'minimum': 0, 'maximum': 1, 'exclusiveMinimum': 0},
    {'type': 'string', 'pattern': '^x$'},
])
def test_supported_keyword_conjunctions_and_deep_json_equality_match_independent_oracle(node):
    definitions = {'Planning': node}
    predicate = schema_predicate.compile_reference(BASE, definitions, 'Planning')
    oracle = original(node)
    assert predicate is not None
    for value in [None, True, False, -0., 0, 1, 1., -1, .5, 2, '', 'x', 'x\n', [], [True, 1],
                  [1, 1.], [{'x': True}, {'x': 1}], {'x': True}, {'x': 1}, {'x': .5, 'y': 3}]:
        assert predicate(value) == oracle.is_valid(value), (node, value)


def outcome(function, document):
    try:
        function('event', document)
        return 'accepted'
    except Exception as error:
        return type(error).__name__, str(error)


def full_original(kind, document):
    root = json.loads((RESOURCES / (kind + '.v2.schema.json')).read_bytes())
    errors = sorted(original(root).iter_errors(document), key=lambda e: str(list(e.path)))
    if errors:
        error = errors[0]
        raise DocumentError(f"{kind} v2 at /{'/'.join(map(str, error.path))}: {error.message}")
    return document


def test_whole_native_positive_path_really_invokes_certificate(monkeypatch):
    validator = schema.all_validators()['event', 2]
    owner = validator._otqa_reference_reuse
    ref = PREFIX + 'PlanningAttempt'
    native = owner.predicates[ref]
    hits = []
    def counted(value):
        result = native(value)
        hits.append(result)
        return result
    monkeypatch.setitem(owner.predicates, ref, counted)
    assert schema.validate('event', event())
    assert True in hits, 'compiled native success path must actually be active'


def test_negative_native_inputs_keep_the_full_original_error_message_and_order():
    for field in ('requested_depth', 'evaluated_horizons', 'selected_plan', 'horizon_evidence'):
        for invalid in [None, True, -1, 4, '', [], {}, math.nan, math.inf]:
            document = event()
            document['payload']['attempt'][field] = deepcopy(invalid)
            actual = outcome(schema.validate, document)
            expected = outcome(full_original, document)
            assert actual == expected


def test_changed_nested_keyword_callback_is_executed_in_full_original_path(monkeypatch):
    document = event()
    plan = document['payload']['attempt']['selected_plan']
    plan['selected']['score'] = {'kind': 'reduction_per_query', 'expected_queries': 1.5,
        'expected_terminal_candidates': 2., 'expected_terminal_loss': 2., 'gain': 1., 'rate': 2/3}
    plan['horizons'][0]['plan']['score'] = plan['selected']['score']
    validator = schema.all_validators()['event', 2]
    marker = RuntimeError('exclusiveMinimum callback must not be bypassed')
    def changed(*args):
        raise marker
    monkeypatch.setitem(validator.VALIDATORS, 'exclusiveMinimum', changed)
    with pytest.raises(RuntimeError) as caught:
        schema.validate('event', document)
    assert caught.value is marker
