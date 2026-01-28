from difflib import get_close_matches
from .base import BaseMappingStrategy
from typing import Dict, List


class FuzzyMatchMappingStrategy(BaseMappingStrategy):

    def map(
        self, mapping: Dict[str, str | None], source_columns: List[str]
    ) -> Dict[str, str | None]:
        for target, mapped_source in mapping.items():
            if mapped_source is None:
                mapping[target] = self.match(target, source_columns)
        return mapping

    @staticmethod
    def match(target: str, source_columns: List[str]) -> str | None:
        matches = get_close_matches(target, source_columns, n=1, cutoff=0.5)

        if matches:
            return matches[0]

        return None
