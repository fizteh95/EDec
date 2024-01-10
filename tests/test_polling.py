import pytest

from src.domain.processors import AbstractAdapter


@pytest.mark.asyncio
async def test_create_retrieve_poll(fake_db_adapter: AbstractAdapter) -> None:
    ...


@pytest.mark.asyncio
async def test_make_vote(fake_db_adapter: AbstractAdapter) -> None:
    ...
