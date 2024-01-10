import pytest

from src.domain.models import SimplePoll
from src.domain.models import SimpleVariant
from src.domain.models import SimpleVote
from src.domain.processors import AbstractAdapter


class FakeDbAdapter(AbstractAdapter):
    def __init__(self) -> None:
        self.polls: dict[str, SimplePoll] = {}
        self.votes: dict[str, SimpleVote] = {}
        self.variants: dict[str, SimpleVariant] = {}

    async def create_poll(
        self,
        creator_id: str,
        name: str,
        description: str,
        is_open: bool,
        variants: list[str],
    ) -> SimplePoll:
        new_poll = SimplePoll(
            poll_id="0",
            creator_id=creator_id,
            name=name,
            description=description,
            is_open=is_open,
            variants=[],
        )
        ...
        return new_poll

    async def get_polls(self, polls_ids: list[str]) -> list[SimplePoll]:
        raise NotImplementedError

    async def create_vote(self, vote: SimpleVote) -> bool:
        raise NotImplementedError

    async def get_poll_results(
        self, poll_id: str, sender_user_id: str
    ) -> dict[str, int]:
        return {}

    async def update_poll(self, poll_id: str, is_open: bool) -> bool:
        raise NotImplementedError


@pytest.fixture
def fake_db_adapter() -> AbstractAdapter:
    fake_adapter = FakeDbAdapter()
    return fake_adapter
