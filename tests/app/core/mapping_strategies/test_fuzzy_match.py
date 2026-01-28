from app.core.mapping_strategies.fuzzy_match import FuzzyMatchMappingStrategy


def test_map_in_fuzzy_match_way(empty_mapping):
    source_columns = ["user_____name", "em@il", "completely_random_column"]
    strat = FuzzyMatchMappingStrategy()
    result = strat.map(empty_mapping, source_columns)

    expected = {"username": "user_____name", "email": "em@il", "phone_number": None}
    assert result == expected
