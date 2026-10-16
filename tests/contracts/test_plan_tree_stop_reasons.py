"""Internal singleton tags must project to the existing native tree vocabulary."""
from copy import deepcopy
from uuid import uuid4

import pytest

from otqa.models.core import Query
from otqa.models.planning import (
    BranchEvaluation, Continuation, EfficiencyScore, FixedScore, PlanningDecision,
    PolicyOption, QueryEvaluation,
)
from otqa.runtime.codec import DocumentError, mathematical_hex
from otqa.runtime.schema import validate
from otqa.runtime.serialization import planning_wire


def _decision(horizon, stop_aware):
    query = Query(0, 1, 1.)
    branches = tuple(
        BranchEvaluation(answer, probability, float(probability > 0),
            1 if probability else None, bool(probability),
            float(probability > 0) if stop_aware else None,
            'single_candidate' if probability else None,
            1. if probability and stop_aware else None,
            0. if stop_aware else None)
        for answer, probability in (('<', .5), ('=', 0.), ('>', .5))
    )
    evaluation = QueryEvaluation(query, 1., branches,
        expected_terminal_loss=1. if stop_aware else None)
    continuations = ()
    if horizon > 1:
        # H3 child-frontier terminals use this PolicyOption shape. Its domain
        # reason intentionally stays unchanged when it becomes a continuation.
        option = PolicyOption(None, 1., 1., 0., stop_reason='single_candidate',
            maximum_volume_share=1. if stop_aware else None)
        continuations = tuple(
            Continuation(answer, .5, 1, option.expected_terminal_candidates,
                option.evaluation, option.expected_terminal_loss if stop_aware else None,
                option.stop_reason, option.maximum_volume_share, option.expected_queries)
            for answer in ('<', '>')
        )
    score = (EfficiencyScore(1., 1., 1., 1., 1.) if horizon == 3
             else FixedScore(1., 1., (1.,), 1.))
    return PlanningDecision(query, horizon, score,
        tuple((branch.answer, branch.probability) for branch in branches),
        evaluation, continuations)


def _event(planning, version):
    payload = {'state_before_index': 0, 'planning': planning}
    return {'schema_version': version, 'run_id': str(uuid4()),
        'attempt_id': 'attempt0001', 'sequence': 1,
        'occurred_at_utc': '2026-10-16T06:00:00Z', 'monotonic_ns': 1,
        'event_type': 'query_planned', 'query_id': 'q000001',
        'payload': payload, 'numeric_hex': mathematical_hex(payload, '/payload')}


@pytest.mark.parametrize('horizon', [1, 2, 3],
    ids=['h1-terminal-branch', 'h2-continuation', 'h3-singleton-option'])
@pytest.mark.parametrize('stop_aware', [False, True])
def test_full_tree_singleton_reasons_follow_native_contract(horizon, stop_aware):
    decision = _decision(horizon, stop_aware)
    planning = planning_wire(decision, stop_aware=stop_aware,
        trace_level='full', candidate_count=2)
    children = [branch['child'] for branch in planning['plan_tree']['branches']
                if branch['probability'] > 0]
    assert len(children) == 2
    assert all(child['stop_reason'] == 'exact_single_candidate' for child in children)
    # Existing v1 documents and the v2 tree contract use the same public tag.
    for version in (1, 2):
        validate('event', _event(planning, version))
    assert all(branch.stop_reason == 'single_candidate'
        for branch in decision.evaluation.branches if branch.probability > 0)
    assert all(child.stop_reason == 'single_candidate' for child in decision.continuations)


def test_tree_schemas_continue_rejecting_internal_singleton_tag():
    planning = planning_wire(_decision(2, True), stop_aware=True,
        trace_level='full', candidate_count=2)
    broken = deepcopy(planning)
    broken['plan_tree']['branches'][0]['child']['stop_reason'] = 'single_candidate'
    for version in (1, 2):
        with pytest.raises(DocumentError):
            validate('event', _event(broken, version))
