import pytest
import sqlite3
import json
from app.core.repository import SQLiteRepository


@pytest.fixture
def repo(tmp_path):
    db_file = tmp_path / "test_mapping.db"
    return SQLiteRepository(str(db_file))


def test_init_db_creates_table(tmp_path):
    """Verify that initialization creates the schema correctly."""
    db_file = tmp_path / "init_test.db"
    repo = SQLiteRepository(str(db_file))

    with sqlite3.connect(str(db_file)) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='mappings'"
        )
        assert cursor.fetchone() is not None


def test_insert_new_mapping(repo):
    test_name = "test_template"
    test_mapping = {"user_id": "ID_Col", "email": "Email_Col"}

    repo.save_mapping(test_name, test_mapping)

    with sqlite3.connect(repo.db_path) as conn:
        cursor = conn.execute(
            "SELECT * FROM mappings WHERE name = ? and mapping_json = ?",
            (test_name, json.dumps(test_mapping)),
        )
        assert cursor.fetchone() is not None


def test_get_mapping(repo):
    test_name = "test_template"
    test_mapping = {"user_id": "ID_Col", "email": "Email_Col"}

    with sqlite3.connect(repo.db_path) as conn:
        conn.execute(
            "INSERT INTO mappings (name, mapping_json) VALUES (?, ?)",
            (test_name, json.dumps(test_mapping)),
        )
    result = repo.get_mapping(test_name)
    assert result == test_mapping


def test_get_non_existent_mapping(repo):
    assert repo.get_mapping("Nothing") is None
