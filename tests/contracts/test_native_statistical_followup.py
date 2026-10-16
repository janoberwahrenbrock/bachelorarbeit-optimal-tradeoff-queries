"""Prospective fixed-N decision rules and complete ordering, no solver calls."""
from copy import deepcopy
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
import math
from pathlib import Path

import pytest

SPEC = spec_from_file_location('_followup_under_test', Path(__file__).resolve().parents[2] / 'tools/validation/compare_native_statistical_followup.py')
subject = module_from_spec(SPEC)
SPEC.loader.exec_module(subject)


def plan():
    conditions = subject.original.conditions()
    rounds, first, jobs = subject.schedule([c['condition_id'] for c in conditions])
    return {'conditions': conditions, 'cases': subject.original.cases(), 'seed': subject.SEED,
        'jobs': jobs, 'round_condition_order': rounds, 'first_variant_by_condition': first,
        'paired_blocks': list(range(1, 31)), 'conditional_extra_blocks': [],
        'harness_sha256': subject.ORIGINAL_SHA,
        'source_probes': {'new': {'source': {'source_sha256': subject.NEW_SOURCE}}},
        'profiles': {'new': {'sha256': subject.NEW_PROFILE}}}


def test_exact_sign_boundary_and_strict_ties():
    assert subject.exact_tail(22) > Fraction(1, 240) >= subject.exact_tail(23)
    assert subject.exact_tail(30) == Fraction(1, 2**30)
    assert subject.exact_tail(0) == 1
    assert not subject.classify([1.] * 22 + [1.05] * 8)['passed']
    outcome = subject.classify([1.] * 23 + [1.05] * 7)
    assert outcome['passed'] and outcome['strictly_below'] == 23 and outcome['ties_fail'] == 7 and outcome['above'] == 0
    below = math.nextafter(1.05, -math.inf)
    above = math.nextafter(1.05, math.inf)
    outcome = subject.classify([below] * 23 + [above] * 7)
    assert outcome['passed'] and outcome['strictly_below'] == 23 and outcome['above'] == 7


@pytest.mark.parametrize('bad', [[1.] * 29, [1.] * 31, [1.] * 29 + [math.nan], [1.] * 29 + [math.inf], [1.] * 29 + [0.], [1.] * 29 + [True]])
def test_invalid_or_partial_timings_never_qualify(bad):
    with pytest.raises(ValueError):
        subject.classify(bad)


def test_complete_seeded_schedule_is_balanced_and_fully_specified_before_calls():
    value = plan()
    subject.validate_plan(value)
    assert len(value['jobs']) == len({j['job_id'] for j in value['jobs']}) == 720
    assert len({(j['condition_id'], j['block']) for j in value['jobs']}) == 360
    for first in value['first_variant_by_condition'].values():
        assert first.count('old') == first.count('new') == 15
    for a, b in zip(value['jobs'][::2], value['jobs'][1::2]):
        assert (a['condition_id'], a['block']) == (b['condition_id'], b['block'])
        assert {a['variant'], b['variant']} == {'old', 'new'}
    assert subject.schedule([c['condition_id'] for c in value['conditions']]) == (value['round_condition_order'], value['first_variant_by_condition'], value['jobs'])


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'reorder', 'seed', 'extension', 'case'])
def test_missing_duplicate_changed_order_or_scope_cannot_match_the_fixed_plan(mutation):
    value = deepcopy(plan())
    if mutation == 'missing':
        value['jobs'].pop()
    elif mutation == 'duplicate':
        value['jobs'][-1] = value['jobs'][0]
    elif mutation == 'reorder':
        value['jobs'][0], value['jobs'][1] = value['jobs'][1], value['jobs'][0]
    elif mutation == 'seed':
        value['seed'] += 1
    elif mutation == 'extension':
        value['conditional_extra_blocks'] = [31]
    else:
        value['cases']['analytic-g2-a3']['weights'][0] += .01
    with pytest.raises(ValueError):
        subject.validate_plan(value)


@pytest.mark.parametrize('extra', [[], [.5] * 30, [2.] * 30, [.5, 1.05, 2.] * 20])
def test_original_max_rule_crossing_is_absorbing(extra):
    assert subject.original.screening([1., 1.1] + extra) == 'inconclusive'


def test_invalid_native_receipts_are_ineligible():
    receipt = {'verified': True, 'cli_returncode': 0, 'reader_returncode': 0, 'status': 'completed',
        'solved': True, 'fallbacks': 0, 'quality': {'selected_correct': True, 'actual_answers_correct': True}}
    assert subject.valid_receipt(receipt)
    for field, value in [('verified', False), ('cli_returncode', 1), ('reader_returncode', 1), ('solved', False), ('fallbacks', 1)]:
        altered = {**receipt, field: value}
        assert not subject.valid_receipt(altered)
    assert subject.protocol()['unconditional_95_percent_guarantee'] is False if 'unconditional_95_percent_guarantee' in subject.protocol() else 'No unconditional95%' in subject.protocol()['multiplicity']
