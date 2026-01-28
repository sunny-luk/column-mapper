from .base import BaseMappingStrategy
from typing import Dict, List


class CaseInsensitiveMappingStrategy(BaseMappingStrategy):
    def map(
        self, mapping: Dict[str, str | None], source_columns: List[str]
    ) -> Dict[str, str | None]:
        lower_source_columns = {col.lower(): col for col in source_columns}

        for target, mapped_source in mapping.items():
            if mapped_source is None:
                mapping[target] = lower_source_columns.get(target.lower())

        return mapping
