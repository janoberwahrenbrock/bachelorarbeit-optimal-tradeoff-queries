import pytest

from otqa.config import AlgorithmPolicy, SingleCandidateStop
from otqa.geometry import GeometrySession
from otqa.models import Problem, Query, AnsweredQuery
from otqa.queries import already_answered, canonical_key, deduplicate_mirrors, generate_queries
from otqa.state import StateEngine


def test_mirror_dedup_retains_first_orientation_and_orders_output():
    queries = [Query(1, 0, .5), Query(0, 1, 2.), Query(0, 1, 3.)]
    assert deduplicate_mirrors(queries) == [Query(0, 1, 3.), Query(1, 0, .5)]
    assert canonical_key(Query(1, 0, .5)) == (0, 1, 2.)
    events = []
    assert deduplicate_mirrors(queries, capture_filter=lambda *event: events.append(event)) == deduplicate_mirrors(queries)
    assert any(reason == "mirror_duplicate" and not retained for reason, _, retained in events)


def test_answer_filter_detects_direct_and_reciprocal_questions():
    history = (AnsweredQuery(Query(0, 1, 2.), ">"),)
    assert already_answered(Query(0, 1, 2.), history)
    assert already_answered(Query(1, 0, .5), history)
    assert not already_answered(Query(0, 1, 3.), history)


@pytest.mark.parametrize("source", ["grid", "both"])
def test_final_level_always_uses_ratios_and_higher_level_uses_policy(source):
    problem = Problem(((1., 0.), (0., 1.)))
    policy = AlgorithmPolicy("fixed", 2, source, 5, "candidate_count", SingleCandidateStop())
    with GeometrySession() as geometry:
        state = StateEngine(problem, policy, geometry).initial()
        final = generate_queries(state, 1)
        higher = generate_queries(state, 2)
        assert set(final.query_sources.values()) == {"ratio"}
        assert "grid" in set(higher.query_sources.values())
        if source == "grid":
            assert set(higher.query_sources.values()) == {"grid"}
        else:
            assert "ratio" in set(higher.query_sources.values())
        assert higher.ratio_intervals_by_goal_pair is not None


def test_filter_capture_records_existing_decisions_without_extra_lp_or_query_changes():
    problem = Problem(((1., 0.), (0., 1.)))
    policy = AlgorithmPolicy("fixed", 2, "both", 5, "candidate_count", SingleCandidateStop())
    with GeometrySession() as geometry:
        engine = StateEngine(problem, policy, geometry)
        state = engine.initial()
        start = geometry.backend.calls
        plain = generate_queries(state, 2)
        plain_calls = geometry.backend.calls - start
        events = []
        start = geometry.backend.calls
        captured = generate_queries(state, 2, capture_filter=lambda *event: events.append(event))
        assert geometry.backend.calls - start == plain_calls
        assert captured == plain
        assert {"source_grid", "source_ratio", "already_answered"}.issubset({event[0] for event in events})
