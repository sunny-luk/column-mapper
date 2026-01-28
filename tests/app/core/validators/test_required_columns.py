import pytest
from app.core.validators.required_columns import RequiredColumnsValidator
from app.core.validators.exceptions import ValidationException


def test_no_missing_required_columns(dummy_schema):
    validator = RequiredColumnsValidator()
    mapping = {"username": "u", "email": "e"}
    validator.validate(mapping, dummy_schema)


def test_missing_required_columns(dummy_schema):
    validator = RequiredColumnsValidator()
    mapping = {"phone_number": "p"}

    expected_error_message = "Missing required mappings for: email, username"
    with pytest.raises(ValidationException, match=expected_error_message):
        validator.validate(mapping, dummy_schema)
