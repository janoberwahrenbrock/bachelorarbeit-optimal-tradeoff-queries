"""A max-gain witness is an evaluated plan, not a claimed rate winner."""
from dataclasses import replace
import pytest
from otqa.models.core import Query
from otqa.models.planning import EfficiencyScore, HorizonEvidence, PlanningDecision, QueryEvaluation
from otqa.models.execution import HorizonSelectionEvidence, PlanningAttempt, ProgressEvidence
from otqa.runtime.codec import DocumentError
from otqa.runtime.journal import _attempt, validate_planning
from otqa.runtime.serialization import attempt_wire


def example():
    rate_query, gain_query = Query(0, 1, 1.), Query(0, 1, .5)
    rate_score = EfficiencyScore(1.4, 1.4, 1., 2. - 1.4, (2. - 1.4) / 1.)
    gain_score = EfficiencyScore(1., 1., 2., 1., .5)
    rate_eval = QueryEvaluation(rate_query, 1.4, (), expected_terminal_loss=1.4)
    gain_eval = QueryEvaluation(gain_query, 1., (), expected_terminal_loss=1.)
    probabilities = (('<', .5), ('=', 0.), ('>', .5))
    # Both decisions retain the actual per-horizon rate-winner summaries.
    summary = HorizonEvidence(2, (rate_eval, gain_eval), rate_query, rate_score, probabilities)
    selected = PlanningDecision(rate_query, 2, rate_score, probabilities, rate_eval, horizons=(summary,))
    witness = replace(selected, query=gain_query, score=gain_score, evaluation=gain_eval)
    selected_progress = ProgressEvidence('candidate_count', 2., 1.4, 2. - 1.4, .001)
    witness_progress = ProgressEvidence('candidate_count', 2., 1., 1., .001)
    horizon = HorizonSelectionEvidence(2, 2, 2, 'available', selected, selected_progress, witness, witness_progress)
    attempt = PlanningAttempt(2, (2,), 'available', selected, selected_progress, witness, (horizon,))
    policy = {'query_strategy': 'reduction_per_query', 'depth': 2, 'planning_evaluation': 'candidate_count',
              'min_expected_progress': .001}
    return attempt, policy


def test_same_horizon_gain_witness_different_from_rate_winner_is_self_contained():
    attempt, policy = example()
    # Isolate horizon two; a complete adaptive depth-two attempt also covers one.
    horizon_one = HorizonSelectionEvidence(1, 0, 0, 'no_query')
    attempt = replace(attempt, evaluated_horizons=(1, 2), horizon_evidence=(horizon_one, *attempt.horizon_evidence))
    # Actual selected plans include the no-query evidence for required horizon one.
    empty = HorizonEvidence(1, (), None)
    summary = attempt.selected_plan.horizons[0]
    selected = replace(attempt.selected_plan, horizons=(empty, summary))
    witness = replace(attempt.best_progress_witness, horizons=(empty, summary))
    h2 = replace(attempt.horizon_evidence[1], selected_plan=selected, best_progress_witness=witness)
    attempt = replace(attempt, selected_plan=selected, best_progress_witness=witness, horizon_evidence=(horizon_one, h2))
    wire = attempt_wire(attempt, stop_aware=False, trace_level='standard')
    assert wire['selected_plan']['selected']['score']['rate'] > wire['best_progress_witness']['selected']['score']['rate']
    assert wire['selected_plan']['selected']['query'] != wire['best_progress_witness']['selected']['query']
    validate_planning(wire['best_progress_witness'])
    validate_planning(wire['horizon_evidence'][1]['best_progress_witness'])
    _attempt(wire, policy, 2)


@pytest.mark.parametrize('outcome,generated,evaluated', [('no_query', 1, 0), ('available', 3, 2)])
def test_unevaluated_generated_queries_cannot_claim_complete_horizon(outcome, generated, evaluated):
    attempt, policy = example()
    wire = attempt_wire(attempt, stop_aware=False, trace_level='standard')
    policy['query_strategy'] = 'fixed'  # scope is coverage, before score interpretation
    horizon = wire['horizon_evidence'][0]
    horizon.update(outcome=outcome, generated_query_count=generated, evaluated_query_count=evaluated)
    with pytest.raises(DocumentError, match='complete generated query inventory'):
        _attempt(wire, policy, 2)
