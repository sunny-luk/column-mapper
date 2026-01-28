import pytest
import pandas as pd
from io import BytesIO, StringIO
from pathlib import Path
from app.core.csv_service import CSVService


@pytest.fixture
def csv_service(tmp_path):
    """Uses a temporary directory for test file storage."""
    return CSVService(storage_path=tmp_path)


def test_save_upload(csv_service):
    content = b"id,name\n1,test"
    file_obj = BytesIO(content)
    file_name = "test_file.csv"

    saved_path = csv_service.save_upload(file_name, file_obj)

    assert saved_path.exists()
    assert saved_path.read_bytes() == content


def test_get_columns_with_header(csv_service, tmp_path):
    file_path = tmp_path / "header.csv"
    file_path.write_text("user_id,email,status\n1,a@b.com,active")

    cols = csv_service.get_columns(file_path, has_header=True)
    assert cols == ["user_id", "email", "status"]


def test_get_columns_without_header(csv_service, tmp_path):
    file_path = tmp_path / "no_header.csv"
    file_path.write_text("1,a@b.com,active")  # Data but no names

    cols = csv_service.get_columns(file_path, has_header=False)
    assert cols == ["column_0", "column_1", "column_2"]
