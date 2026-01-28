import os
import time
import pandas as pd
import shutil
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class CSVService:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

    def save_upload(self, file_name: str, file_obj) -> Path:
        """
        Streams the file object to disk to handle up to 100MB safely.
        """
        target_path = self.storage_path / self._generate_file_name(file_name)
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)
        return target_path

    @staticmethod
    def _generate_file_name(file_name: str) -> str:
        """
        Append current timestamp for name uniqueness (naive approach)
        """
        extension = file_name.split(".")[-1]
        file_name_part = file_name[: -len(extension) + 1]
        return file_name_part + str(int(time.time())) + f".{extension}"

    def get_columns(self, file_path: Path, has_header: bool = True) -> List[str]:
        """
        Extracts columns. If no header, generates generic column_n names.
        Uses nrows=0 for speed and memory efficiency.
        """
        try:
            if has_header:
                # nrows=0 reads only the header row
                df = pd.read_csv(file_path, nrows=0)
                return df.columns.tolist()
            else:
                # Read 1 row to count columns, then generate names
                df = pd.read_csv(file_path, nrows=1, header=None)
                return [f"column_{i}" for i in range(len(df.columns))]
        except Exception as e:
            logger.error(f"Failed to parse columns: {e}")
            return []
