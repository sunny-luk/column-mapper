from .base import BaseValidator
from .exceptions import ValidationException


class RequiredColumnsValidator(BaseValidator):

    def validate(self, mapping, schema_class):
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
        missing_fields = sorted(list(required_fields - mapped_fields))

        if missing_fields:
            raise ValidationException(
                f"Missing required mappings for: {', '.join(missing_fields)}"
            )

    def validation_category(self) -> str:
        return "Required Mapping"
