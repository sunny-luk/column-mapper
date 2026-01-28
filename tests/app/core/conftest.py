import pytest
from typing import List, Type
from pydantic import BaseModel, EmailStr


@pytest.fixture
def dummy_schema() -> Type[BaseModel]:
    class DummySchema(BaseModel):
        username: str
        email: EmailStr
        phone_number: int = None

    return DummySchema
