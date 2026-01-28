import json
import sqlite3
from abc import ABC, abstractmethod
from typing import Dict


class BaseRepository(ABC):

    @abstractmethod
    def save_mapping(self, name: str, mapping: Dict[str, str]) -> bool:
        pass

    @abstractmethod
    def get_mapping(self, name: str) -> Dict[str, str] | None:
        pass


class SQLiteRepository(BaseRepository):

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    mapping_json TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save_mapping(self, name: str, mapping: Dict[str, str]):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO mappings (name, mapping_json) VALUES (?, ?)",
                (name, json.dumps(mapping)),
            )

    def get_mapping(self, name: str) -> Dict[str, str] | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT mapping_json FROM mappings WHERE name = ?", (name,)
            ).fetchone()
            return json.loads(row[0]) if row else None
