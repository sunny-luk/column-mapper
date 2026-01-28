import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from io import BytesIO
from app.main import app, get_csv_service, get_repository
from app.core.csv_service import CSVService
from app.core.repository import SQLiteRepository

client = TestClient(app)


@pytest.fixture
def test_setup(tmp_path):
    """
    Sets up a temporary environment for each test.
    Overrides the dependencies to use a temp folder and temp DB.
    """
    temp_storage = tmp_path / "csv_storage"
    temp_storage.mkdir()
    temp_db = tmp_path / "test.db"

    # Define the mock services
    mock_csv_service = CSVService(str(temp_storage))
    mock_repo = SQLiteRepository(str(temp_db))

    # Apply overrides
    app.dependency_overrides[get_csv_service] = lambda: mock_csv_service
    app.dependency_overrides[get_repository] = lambda: mock_repo

    yield {"repo": mock_repo, "storage": temp_storage}

    # Clear overrides after the test
    app.dependency_overrides = {}


def test_upload_file_success(test_setup):
    # Prepare dummy CSV data
    # Note: 'UserName' should map to 'username' via CaseInsensitive strategy
    csv_content = b"UserName,Email,Phone\nalice,alice@example.com,12345"
    file_name = "users.csv"

    response = client.post(
        "/upload",
        files={"file": (file_name, BytesIO(csv_content), "text/csv")},
        data={"has_header": "true"},
    )

    assert response.status_code == 201
    data = response.json()

    # Assertions on response structure
    assert data["filename"] == file_name
    assert "username" in data["suggested_mapping"]
    assert data["suggested_mapping"]["username"] == "UserName"

    # Assertions on side effects (File actually exists on disk)
    saved_path = Path(test_setup["storage"]) / data["saved_filename"]
    assert saved_path.exists()


def test_upload_file_too_large(test_setup):
    # Create a 'large' file by manipulating the size attribute if possible,
    # or just sending a large byte string.
    # For a unit test, we can just mock the file object's size.
    large_content = b"x" * (101 * 1024 * 1024)  # 101MB

    response = client.post(
        "/upload", files={"file": ("huge.csv", BytesIO(large_content), "text/csv")}
    )

    assert response.status_code == 413
    assert "exceeds 100MB" in response.json()["detail"]


def test_upload_with_saved_mapping(test_setup):
    # 1. Manually seed a mapping in our temp repo
    repo = test_setup["repo"]
    repo.save_mapping("my_config", {"email": "Custom_Email_Col"})

    # 2. Upload a file referencing that mapping
    csv_content = b"Custom_Email_Col,username\ntest@test.com,user1"
    response = client.post(
        "/upload",
        files={"file": ("test.csv", BytesIO(csv_content), "text/csv")},
        data={"apply_mapping_name": "my_config"},
    )

    assert response.status_code == 201
    # The suggested mapping should prioritize the saved one
    assert response.json()["suggested_mapping"]["email"] == "Custom_Email_Col"


def test_upload_file_no_header(test_setup):
    # 1. Prepare CSV data where row 1 is actual data, not a header
    csv_content = b"jdoe,john@test.com,12345"
    file_name = "no_header_users.csv"

    # 2. Execute POST with has_header set to false
    response = client.post(
        "/upload",
        files={"file": (file_name, BytesIO(csv_content), "text/csv")},
        data={"has_header": "false"},  # Note: form data sends "false" as string
    )

    assert response.status_code == 201
    data = response.json()

    # 3. Assertions
    # Since there are 3 values in the row, we expect 3 synthetic columns
    expected_cols = ["column_0", "column_1", "column_2"]
    assert data["source_columns"] == expected_cols

    # Verify the suggested mapping still attempts to work with these new names
    # (If your strategy handles 'column_n' or just returns empty)
    assert "suggested_mapping" in data


def test_upload_file_mapping_not_found(test_setup):
    """
    Verify that providing a non-existent mapping name returns
    a 400 error instead of a 500 or crashing.
    """
    # 1. Prepare dummy data
    csv_content = b"col1,col2\nval1,val2"
    file_name = "test.csv"
    non_existent_mapping = "i_do_not_exist_in_db"

    # 2. Execute POST with a fake mapping name
    response = client.post(
        "/upload",
        files={"file": (file_name, BytesIO(csv_content), "text/csv")},
        data={"has_header": "true", "apply_mapping_name": non_existent_mapping},
    )

    # 3. Assertions
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert non_existent_mapping in detail
    assert "Could not find saved mapping" in detail
