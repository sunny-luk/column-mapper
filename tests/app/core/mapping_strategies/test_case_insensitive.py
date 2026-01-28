import pytest
from typing import Dict
from app.core.mapping_strategies.case_insensitive import CaseInsensitiveMappingStrategy


@pytest.fixture
def empty_mapping() -> Dict[str, str | None]:
    return {"username": None, "email": None, "phone_number": None}


def test_map_in_case_insensitive_way(empty_mapping):
    source_columns = ["UserName", "EMAIL", "phone"]
    strat = CaseInsensitiveMappingStrategy()
    result = strat.map(empty_mapping, source_columns)

    expected = {"username": "UserName", "email": "EMAIL", "phone_number": None}
    assert result == expected
