import pandas as pd
from .base import BaseValidator
from .exceptions import ValidationException
from ..csv_service import CSVService


class MissingValueColumnsValidator(BaseValidator):

    def __init__(self, filename: str, csv_service: CSVService):
        self.filename = filename
        self.csv_service = csv_service

    def validate(self, mapping, schema_class):
        """
        Checks if all required fields in the Pydantic schema
        are having non-null values in csv
        """
        # Get all fields that don't have a default value (required fields)
        required_fields = {
            name
            for name, field in schema_class.model_fields.items()
            if field.is_required()
        }
        df = self.csv_service.get_file_df(self.filename)

        columns_with_na = set()

        for field in required_fields:
            mapped_column = mapping.get(field)
            if mapped_column and self._check_na_in_column(df, mapped_column):
                columns_with_na.add(mapped_column)

        if columns_with_na:
            raise ValidationException(
                f"NA(s) exist in: {', '.join(sorted(list(columns_with_na)))}"
            )

    @staticmethod
    def _check_na_in_column(df: pd.DataFrame, column: str) -> bool:
        return df[column].isna().any()

    def validation_category(self) -> str:
        return "NA values"
