import pickle

import pytest

from otqa.config import AlgorithmPolicy, SingleCandidateStop
from otqa.geometry import GeometrySession
from otqa.models import Problem, Query, AnsweredQuery
from otqa.state import StateEngine, compute_terminal_candidate_count
from otqa.state import history_key


def policy():
    return AlgorithmPolicy("fixed", 2, "both", 5, "candidate_count", SingleCandidateStop())


def test_dominated_alternative_is_removed_without_reindexing():
    problem = Problem(((1., 0.), (0., 1.), (0., 0.)))
    with GeometrySession() as geometry:
        state = StateEngine(problem, policy(), geometry).initial(need_volumes=True)
        assert state.analysis.candidates == (0, 1)
        assert state.analysis.candidate_volume_shares == pytest.approx({0: .5, 1: .5})


def test_terminal_fastpath_and_full_analysis_agree_for_strict_split():
    problem = Problem(((1., 0.), (0., 1.)))
    with GeometrySession() as geometry:
        engine = StateEngine(problem, policy(), geometry)
        parent = engine.initial()
        query = Query(0, 1, 1.)
        assert compute_terminal_candidate_count(parent, query, "<", .5) == (1, True)
        child = engine.advance(parent, AnsweredQuery(query, "<"), terminal=True)
        assert child.analysis.candidates == (1,)
        assert child.analysis.ratio_intervals is None


def test_prepared_root_transfer_carries_no_native_resources():
    problem = Problem(((1., 0.), (0., 1.)))
    with GeometrySession() as first, GeometrySession() as second:
        engine = StateEngine(problem, policy(), first, session_id="example-scope")
        state = engine.initial()
        transferred = pickle.loads(pickle.dumps(state))
        assert transferred.weight_space.backend is None
        assert not hasattr(transferred.weight_space, "_geometry_owner")
        worker = StateEngine(problem, policy(), second, session_id="example-scope")
        calls = second.backend.calls
        rebound = worker.bind(transferred)
        assert rebound.analysis == state.analysis
        assert second.backend.calls == calls
        assert rebound.weight_space.backend is second.backend
        with pytest.raises(ValueError):
            StateEngine(problem, policy(), second).bind(transferred)


def test_prepared_analysis_and_constraint_payload_are_immutable():
    problem = Problem(((1., 0.), (0., 1.)))
    with GeometrySession() as geometry:
        state = StateEngine(problem, policy(), geometry).initial(need_volumes=True)
        with pytest.raises(TypeError):
            state.analysis.candidate_volumes[0] = 123.
        with pytest.raises(TypeError):
            state.analysis.ratio_intervals[0].intervals_by_candidate[0] = None
        with pytest.raises(TypeError):
            state.analysis.candidate_volumes._data[0] = 123.
        with pytest.raises(AttributeError):
            state.weight_space.add_equality([1., 0.], .5)
        with pytest.raises(AttributeError):
            state.weight_space.equalities_left_side = ()
        with pytest.raises(TypeError):
            state.weight_space.equalities_left_side[0][0] = 2.
        for array in state.weight_space.get_solver_matrices():
            if array is not None:
                with pytest.raises(ValueError):
                    array.setflags(write=True)
        transferred = pickle.loads(pickle.dumps(state))
        assert transferred.weight_space.key == state.weight_space.key
        assert transferred.analysis == state.analysis
        with pytest.raises(AttributeError):
            transferred.weight_space.add_inequality([1., 0.], .7)
        builder = state.weight_space.copy()
        builder.add_inequality([1., 0.], .7)
        assert len(builder.inequalities_left_side) == len(state.weight_space.inequalities_left_side) + 1


def test_history_cache_identity_preserves_signed_zero_and_order():
    positive = (AnsweredQuery(Query(0, 1, 0.), "="),)
    negative = (AnsweredQuery(Query(0, 1, -0.), "="),)
    assert history_key(positive) != history_key(negative)
    assert history_key(positive + negative) != history_key(negative + positive)
    problem = Problem(((1., 0.), (0., 1.)))
    with GeometrySession() as geometry:
        engine = StateEngine(problem, policy(), geometry)
        assert engine.initial(positive).history[0].query.value.hex() == "0x0.0p+0"
        assert engine.initial(negative).history[0].query.value.hex() == "-0x0.0p+0"
