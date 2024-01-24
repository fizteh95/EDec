import pytest

from src.domain.processors import AbstractAdapter
from src.services.db_adapter import FakeDbAdapter


@pytest.fixture
def fake_db_adapter() -> AbstractAdapter:
    fake_adapter = FakeDbAdapter()
    return fake_adapter
