import pandas as pd
from typing import List, Dict
from pydantic import BaseModel


class ValidationService:
    def validate_columns(
        self, mapping: Dict[str, str | None], schema_class: type[BaseModel]
    ) -> List[str]:
        """
        Checks if all required fields in the Pydantic schema
        are present in the user's mapping
        """
        # Get all fields that don't have a default value (required fields)
        required_fields = {
            name
            for name, field in schema_class.model_fields.items()
            if field.is_required()
        }
        mapped_fields = {
            target for target, source in mapping.items() if source is not None
        }

        # Check which required fields are missing from the mapping keys
        missing_fields = list(required_fields - mapped_fields)

        return sorted(missing_fields)
