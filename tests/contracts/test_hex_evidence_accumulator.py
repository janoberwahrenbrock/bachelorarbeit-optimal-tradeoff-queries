"""Independent original-reader comparisons for a single evidence accumulator."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import math
import random

import pytest

from otqa.runtime.codec import mathematical_hex

path = Path(__file__).with_name('fixtures') / 'codec_before_hex_accumulator.py'
spec = spec_from_file_location('otqa.runtime._codec_before_hex_accumulator', path)
REFERENCE = module_from_spec(spec)
spec.loader.exec_module(REFERENCE)


def outcome(function, value, pointer='', all_numbers=False):
    try:
        result = function(value, pointer, all_numbers=all_numbers)
        return ('accepted', list(result.items()))
    except Exception as error:
        return type(error).__name__, str(error)


def test_typed_selection_and_negative_zero_have_analytical_evidence():
    value = {'value': 1, 'n': 2, 'float_outside': 1.5,
        'answer_probabilities': {'<': .25, '=': 0, '>': -0.0},
        'context': {'value': float('nan')}, 'error': {'value': float('inf')}}
    assert mathematical_hex(value, '/payload') == {
        '/payload/value': 1.0.hex(), '/payload/answer_probabilities/<': .25.hex(),
        '/payload/answer_probabilities/=': 0.0.hex(), '/payload/answer_probabilities/>': (-0.0).hex()}


@pytest.mark.parametrize('key', ['value', 'probability', 'expected_terminal_candidates', 'expected_terminal_loss',
    'expected_queries', 'gain', 'rate', 'min_expected_progress', 'starting_value', 'expected_terminal_value',
    'expected_progress', 'threshold', 'maximum_volume_share', 'selected_candidate_volume', 'selected_candidate_volume_share',
    'candidate_volumes', 'candidate_volume_shares', 'answer_probabilities', 'lexicographic_expected_values'])
def test_all_mathematical_names_retain_typed_nested_projection(key):
    value = {key: {'escaped/~key': [1, 1.0, -0.0, True, None, '1', {'sub': 2}]}}
    assert outcome(mathematical_hex, value) == outcome(REFERENCE.mathematical_hex, value)


@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf, 10 ** 400])
@pytest.mark.parametrize('all_numbers', [False, True])
def test_nonfinite_and_overflow_errors_preserve_original_precedence(value, all_numbers):
    for doc in (value, {'value': value}, {'count': value}, {'candidate_volumes': [value]},
                {'error': {'value': value}}, {'value': [True, value]}):
        assert outcome(mathematical_hex, doc, all_numbers=all_numbers) == outcome(
            REFERENCE.mathematical_hex, doc, all_numbers=all_numbers)


def test_all_excluded_fields_remain_excluded_even_with_inherited_number_scope():
    doc = {'value': {key: {'value': math.nan} for key in ('error', 'context', 'telemetry_errors', 'numeric_hex')}}
    assert mathematical_hex(doc) == {}
    assert mathematical_hex(doc, all_numbers=True) == {}


def test_references_tuple_containers_and_mapping_order_remain_equivalent():
    class Number(float):
        pass
    class Mapping(dict):
        pass
    item = Mapping(value=[0.0, -0.0, Number(1.0), 1, True])
    doc = {'answer_probabilities': (item, item), 'value': {'a/b': {'~': 2}}, 'numeric_hex': item}
    for flag in (False, True):
        assert outcome(mathematical_hex, doc, '/a~0b', flag) == outcome(REFERENCE.mathematical_hex, doc, '/a~0b', flag)


def test_non_string_keys_have_the_same_error():
    assert outcome(mathematical_hex, {1: 2}) == outcome(REFERENCE.mathematical_hex, {1: 2})


def random_document(rng, depth):
    values = [None, True, False, -0.0, 0, -1, 1.0, 3.141592653589793, '', 'text/~']
    if depth == 0 or rng.random() < .25:
        return rng.choice(values)
    if rng.random() < .4:
        children = [random_document(rng, depth - 1) for _ in range(rng.randrange(5))]
        return tuple(children) if rng.random() < .25 else children
    keys = ['value', 'probability', 'answer_probabilities', 'lexicographic_expected_values', 'rate',
        'count', 'nested', 'error', 'context', 'telemetry_errors', 'numeric_hex', 'a/b', '~', '']
    return {key: random_document(rng, depth - 1) for key in rng.sample(keys, rng.randrange(6))}


@pytest.mark.parametrize('seed', range(10))
def test_saved_seed_nested_values_match_frozen_original(seed):
    rng = random.Random(2026101600 + seed)
    for _ in range(100):
        doc = random_document(rng, 5)
        before = deepcopy(doc)
        for flag in (False, True):
            assert outcome(mathematical_hex, doc, '/root/~0', flag) == outcome(
                REFERENCE.mathematical_hex, doc, '/root/~0', flag)
        assert doc == before
