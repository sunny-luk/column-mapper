import pytest
from app.core.mapping_engine import MappingEngine
from app.core.mapping_strategies.base import BaseMappingStrategy


@pytest.fixture
def mapping_engine(dummy_schema):
    return MappingEngine(dummy_schema)


class FakeStrategy(BaseMappingStrategy):
    def map(self, mapping, source_columns):
        mapping.update({"email": "e-mail"})
        return mapping


def test_mapping_engine_with_no_saved_mapping(mapping_engine):
    source_columns = ["user", "e-mail", "phone_num"]
    result = mapping_engine.run(
        source_columns=source_columns, mapping_strategy=FakeStrategy()
    )
    expected = {"username": None, "email": "e-mail", "phone_number": None}
    assert result == expected


def test_mapping_engine_with_saved_mapping(mapping_engine):
    source_columns = ["user", "e-mail", "email_address", "phone_num"]
    saved_mapping = {"username": "user", "email": "email_address"}
    result = mapping_engine.run(
        source_columns=source_columns,
        saved_mapping=saved_mapping,
        mapping_strategy=FakeStrategy(),
    )
    expected = {"username": "user", "email": "email_address", "phone_number": None}
    assert result == expected
