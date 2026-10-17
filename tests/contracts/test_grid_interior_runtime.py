"""The public solver and persisted H2 records use the same interior grid."""
import pytest

from otqa import AlgorithmPolicy, Problem, SingleCandidateStop, solve
from otqa.answers import SimulatedAnswers
from otqa.queries import candidates
from otqa.runtime.codec import read_json
from otqa.runtime.validation import verify_result

from test_runtime_policy_readers import recorded_result


EXPECTED_GRID5 = [0.1357208808, 0.3684031499, 1.0, 2.7144176166, 7.3680629973]


def capture_grid(monkeypatch):
    observed = []
    original = candidates.grid_values

    def captured(interval, grid_size, **limits):
        values = original(interval, grid_size, **limits)
        observed.append(tuple(values))
        return values

    monkeypatch.setattr(candidates, 'grid_values', captured)
    return observed


@pytest.mark.parametrize('source', ['grid', 'both'])
@pytest.mark.parametrize('strategy,mode', [
    ('fixed', 'receding'), ('fixed', 'countdown'), ('reduction_per_query', 'receding'),
])
def test_public_h2_solver_uses_interior_grid_in_all_execution_modes(monkeypatch, source, strategy, mode):
    observed = capture_grid(monkeypatch)
    policy = AlgorithmPolicy(strategy, 2, source, 5, 'candidate_count', SingleCandidateStop(),
                             horizon_execution=mode)
    result = solve(Problem(((1., 0.), (0., 1.))), policy, SimulatedAnswers((.7, .3)))
    assert result.exactly_solved and result.selected_candidate_index == 0
    assert observed and observed[0] == pytest.approx(EXPECTED_GRID5, abs=5e-11)
    assert result.queries and 2 in [item.horizon for item in result.queries[0].planning.horizons]


@pytest.mark.parametrize('mode', ['receding', 'countdown'])
def test_persisted_h2_run_binds_active_grid_profile_and_valid_journal(tmp_path, monkeypatch, mode):
    observed = capture_grid(monkeypatch)
    _, root, manifest, payload, envelope = recorded_result(tmp_path, depth=2,
        horizon_execution=mode, min_progress=.001)
    stored = read_json(root / 'manifest.json')
    assert stored == manifest
    profile = stored['numerical_profile']
    assert profile['profile_id'] == 'otqa-exact-v3'
    settings = profile['values']['query_generation']
    assert settings['min_grid_value'] == .05 and settings['max_grid_value'] == 20.
    for key in ('min_grid_value', 'max_grid_value'):
        assert profile['numeric_hex']['/values/query_generation/' + key] == settings[key].hex()
    assert observed and observed[0] == pytest.approx(EXPECTED_GRID5, abs=5e-11)
    assert envelope['solver_result']['solved']
    assert verify_result(root / 'result.json', root, payload) == envelope
