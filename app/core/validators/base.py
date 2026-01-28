from abc import ABC, abstractmethod
from typing import Dict
from pydantic import BaseModel


class BaseValidator(ABC):

    @abstractmethod
    def validate(self, mapping: Dict[str, str | None], schema_class: type[BaseModel]):
        pass

    @abstractmethod
    def validation_category(self) -> str:
        pass
