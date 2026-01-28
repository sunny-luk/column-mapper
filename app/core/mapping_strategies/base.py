from abc import ABC, abstractmethod
from typing import Dict, List


class BaseMappingStrategy(ABC):

    @abstractmethod
    def map(
        self, mapping: Dict[str, str | None], source_columns: List[str]
    ) -> Dict[str, str | None]: ...
