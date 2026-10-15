import pytest

from otqa import AnsweredQuery, Query
from otqa.answers import InteractiveAnswers, ReplayAnswers, SimulatedAnswers
from otqa.errors import InputValidationError, InvalidAnswerError


def test_zero_denominator_uses_multiplication_and_raw_weights():
    provider = SimulatedAnswers((2.0, 0.0, 0.0))
    assert provider(Query(0, 1, 5.0)) == '>'
    assert provider(Query(1, 2, 0.0)) == '='


def test_replay_does_not_replace_a_different_planned_query():
    provider = ReplayAnswers((AnsweredQuery(Query(0, 1, 1.0), '<'),))
    with pytest.raises(InputValidationError, match='differs'):
        provider(Query(0, 1, 0.5))
    assert provider.consumed == 0
    assert provider(Query(0, 1, 1.0)) == '<'
    with pytest.raises(InputValidationError, match='exhausted'):
        provider(Query(0, 1, 1.0))


def test_interactive_does_not_normalize_invalid_provider_text():
    with pytest.raises(InvalidAnswerError):
        InteractiveAnswers(lambda prompt: ' >')(Query(0, 1, 1.0))
