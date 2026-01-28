import pytest
from typing import Dict


@pytest.fixture
def empty_mapping() -> Dict[str, str | None]:
    return {"username": None, "email": None, "phone_number": None}
