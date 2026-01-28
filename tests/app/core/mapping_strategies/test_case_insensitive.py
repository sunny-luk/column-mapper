from app.core.mapping_strategies.case_insensitive import CaseInsensitiveMappingStrategy


def test_map_in_case_insensitive_way(empty_mapping):
    source_columns = ["UserName", "EMAIL", "phone"]
    strat = CaseInsensitiveMappingStrategy()
    result = strat.map(empty_mapping, source_columns)

    expected = {"username": "UserName", "email": "EMAIL", "phone_number": None}
    assert result == expected
