import pytest
from app.core.validation_service import ValidationService


def test_validation_service_checks_for_required_field(dummy_schema):
    service = ValidationService()
    mapping = {"username": None, "email": None, "phone_number": "pn"}
    result = service.validate_columns(mapping, dummy_schema)

    expected = ["username", "email"]
    assert sorted(result) == sorted(expected)
