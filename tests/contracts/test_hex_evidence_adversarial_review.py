"""Independent pure review of depth-first binary64 evidence and error order."""
from collections import OrderedDict, UserDict
from decimal import Decimal
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
import math
from pathlib import Path
import sys
from types import MappingProxyType

import pytest

from otqa.runtime import codec

REFERENCE_PATH = Path(__file__).with_name('fixtures') / 'codec_before_hex_accumulator.py'
SPEC = spec_from_file_location('_independent_frozen_codec', REFERENCE_PATH)
REFERENCE = module_from_spec(SPEC)
SPEC.loader.exec_module(REFERENCE)


def observed(function, value, *, pointer='', all_numbers=False):
    try:
        return ('return', list(function(value, pointer, all_numbers=all_numbers).items()))
    except Exception as exc:
        return ('raise', type(exc).__name__, exc.args)


def test_candidate_module_is_the_isolated_source():
    assert Path(codec.__file__).resolve() == Path(__file__).resolve().parents[2] / 'src/otqa/runtime/codec.py'


@pytest.mark.parametrize('all_numbers', [False, True])
@pytest.mark.parametrize('value', [
    {'value': [False, True, 0, -0.0, 2**53 + 1, 2**1023]},
    {'value': (float.fromhex('0x0.0000000000001p-1022'), sys.float_info.max)},
    {'value': [Decimal('NaN'), Fraction(1, 3), complex(1, 2)]},
    {'n': [math.nan, math.inf, -math.inf], 'threshold': 0},
    {'value': {'error': math.nan, 'context': math.inf, 'numeric_hex': -math.inf,
               'telemetry_errors': 2**1024, 'kept': 1}},
    {'value': {'': [1, {'a~/b': -0.0}]}},
    MappingProxyType({'value': math.nan}),
    UserDict({'value': math.nan}),
])
def test_exact_types_subnormals_exclusions_and_unknown_mappings(value, all_numbers):
    assert observed(codec.mathematical_hex, value, pointer='/raw/~prefix', all_numbers=all_numbers) == observed(
        REFERENCE.mathematical_hex, value, pointer='/raw/~prefix', all_numbers=all_numbers)


def test_analytical_pointer_order_and_signed_zero():
    document = OrderedDict([
        ('a~/b', {'value': (True, -0.0, 0, 2**53 + 1)}),
        ('answer_probabilities', OrderedDict([('=', 0), ('<', .25), ('>', .75)])),
    ])
    assert list(codec.mathematical_hex(document, '/payload').items()) == [
        ('/payload/a~0~1b/value/1', '-0x0.0p+0'),
        ('/payload/a~0~1b/value/2', '0x0.0p+0'),
        ('/payload/a~0~1b/value/3', float(2**53 + 1).hex()),
        ('/payload/answer_probabilities/=', '0x0.0p+0'),
        ('/payload/answer_probabilities/<', '0x1.0000000000000p-2'),
        ('/payload/answer_probabilities/>', '0x1.8000000000000p-1'),
    ]


@pytest.mark.parametrize('name', ['error', 'context', 'telemetry_errors', 'numeric_hex'])
def test_excluded_child_is_never_observed_even_in_inherited_scope(name):
    class Poison(dict):
        def items(self):
            raise AssertionError('excluded mapping must not be traversed')
    value = {'value': {name: Poison(value=math.nan), 'retained': 7}}
    assert codec.mathematical_hex(value, all_numbers=True) == {'/value/retained': 7.0.hex()}
    assert observed(codec.mathematical_hex, value, all_numbers=True) == observed(
        REFERENCE.mathematical_hex, value, all_numbers=True)


@pytest.mark.parametrize('first,second', [
    (('value', math.nan), (1, 2)),
    ((1, 2), ('value', math.nan)),
    (('value', 2**1024), ('probability', math.inf)),
    (('probability', math.inf), ('value', 2**1024)),
])
def test_first_error_and_arguments_follow_mapping_iteration(first, second):
    value = OrderedDict([first, second])
    assert observed(codec.mathematical_hex, value) == observed(REFERENCE.mathematical_hex, value)


def test_number_subclasses_are_never_coerced():
    class Int(int):
        def __float__(self):
            raise AssertionError('int subclass must remain outside exact-number evidence')
    class Float(float):
        def __float__(self):
            raise AssertionError('float subclass must remain outside exact-number evidence')
    document = {'value': [Int(3), Float(math.nan), True, False, 4]}
    assert codec.mathematical_hex(document, all_numbers=True) == {'/value/4': 4.0.hex()}


def test_custom_dict_items_are_visited_once_in_original_depth_first_order():
    def run(function):
        trace = []
        class Mapping(dict):
            def __init__(self, label, pairs):
                super().__init__()
                self.label, self.pairs = label, pairs
            def items(self):
                trace.append(('items', self.label))
                for key, value in self.pairs:
                    trace.append(('yield', self.label, key))
                    yield key, value
        child = Mapping('child', [('value', 1), ('probability', -0.0)])
        document = Mapping('root', [('nested', child), ('value', (child, 2))])
        return observed(function, document), trace
    assert run(codec.mathematical_hex) == run(REFERENCE.mathematical_hex)


def test_pointer_collisions_preserve_first_insertion_order_and_last_value():
    class AliasKey(str):
        def replace(self, old, new):
            return 'same'
    class Mapping(dict):
        def items(self):
            yield AliasKey('first'), OrderedDict([('z', 1), ('y', 2)])
            yield AliasKey('second'), OrderedDict([('y', 3), ('x', 4)])
    document = {'candidate_volumes': Mapping()}
    expected = [('/candidate_volumes/same/z', 1.0.hex()),
                ('/candidate_volumes/same/y', 3.0.hex()),
                ('/candidate_volumes/same/x', 4.0.hex())]
    assert list(codec.mathematical_hex(document).items()) == expected
    assert list(REFERENCE.mathematical_hex(document).items()) == expected


def test_fresh_results_and_shared_children_never_share_an_accumulator():
    child = {'value': -0.0}
    document = {'value': [child, child]}
    first = codec.mathematical_hex(document)
    first['changed'] = 'not evidence'
    second = codec.mathematical_hex(document)
    assert first is not second and 'changed' not in second
    assert second == {'/value/0/value': (-0.0).hex(), '/value/1/value': (-0.0).hex()}
    assert child == {'value': -0.0}


@pytest.mark.parametrize('pointer', ['', '/explicit', 0, None])
def test_leaf_pointer_argument_preserves_existing_behavior(pointer):
    assert observed(codec.mathematical_hex, -0.0, pointer=pointer, all_numbers=True) == observed(
        REFERENCE.mathematical_hex, -0.0, pointer=pointer, all_numbers=True)
