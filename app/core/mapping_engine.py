import logging
from pydantic import BaseModel
from typing import Dict, List, Type
from .mapping_strategies.base import BaseMappingStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MappingEngine:

    def __init__(self, schema: Type[BaseModel]):
        self.schema = schema

    def run(
        self,
        source_columns: List[str],
        saved_mapping: Dict[str, str | None] | None = None,
        mapping_strategy: BaseMappingStrategy | None = None,
    ) -> Dict[str, str | None]:
        """
        Docstring for run

        :param self: self
        :param source_columns: Columns of ingested source data
        :type source_columns: List[str]
        :param saved_mapping: Previously saved mapping that will be applied to result
        :type saved_mapping: Dict[str, str | None] | None
        :param mapping_strategy: Description
        :type mapping_strategy: BaseMappingStrategy
        :return: Mapping contains mapped result after apply previously saved mapping
            and selected mapping strategy
        :rtype: Dict[str, str | None]
        """
        result = {target: None for target in self.schema.model_fields}

        if mapping_strategy:
            result = mapping_strategy.map(result, source_columns)

        if saved_mapping:
            updates = {
                target: source
                for target, source in saved_mapping.items()
                if target in result
            }
            result.update(updates)

        return result
