import re
import pytest
import pandas as pd
from app.core.validators.missing_value_columns import MissingValueColumnsValidator
from app.core.validators.exceptions import ValidationException
from app.core.csv_service import CSVService
from unittest.mock import MagicMock


@pytest.fixture
def mock_csv_service():
    mock = MagicMock(spec=CSVService)
    return mock


def test_no_missing_value_columns(dummy_schema, mock_csv_service):
    mock_csv_service.get_file_df.return_value = pd.DataFrame(
        [
            [
                ["user-1", "user-1@email.com", "12351521"],
                ["user-2", "user-2@email.com", "12351522"],
                ["user-3", "user-3@email.com", "12351523"],
            ]
        ],
        columns=["u", "e", "p"],
    )
    validator = MissingValueColumnsValidator("file.csv", mock_csv_service)
    mapping = {"username": "u", "email": "e", "phone_number": "p"}
    validator.validate(mapping, dummy_schema)


def test_has_missing_value_columns(dummy_schema, mock_csv_service):
    mock_csv_service.get_file_df.return_value = pd.DataFrame(
        [
            ["user-1", "user-1@email.com", "12351521"],
            [pd.NA, "user-2@email.com", "12351522"],
            ["user-3", pd.NA, "12351523"],
        ],
        columns=["u", "e", "p"],
    )
    validator = MissingValueColumnsValidator("file.csv", mock_csv_service)
    mapping = {"username": "u", "email": "e", "phone_number": "p"}
    expected_error_message = "NA(s) exist in: e, u"
    with pytest.raises(ValidationException, match=re.escape(expected_error_message)):
        validator.validate(mapping, dummy_schema)
