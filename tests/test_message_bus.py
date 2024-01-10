import pytest

from src.domain.events import GetPollResult
from src.domain.events import PollResult
from src.domain.processors import AbstractAdapter
from src.domain.processors import VoteCounter
from src.services.message_bus import ConcreteMessageBus


@pytest.mark.asyncio
async def test_message_bus(fake_db_adapter: AbstractAdapter) -> None:
    vote_counter = VoteCounter(db_adapter=fake_db_adapter)

    bus = ConcreteMessageBus()
    bus.register(vote_counter)

    test_call = GetPollResult(
        poll_id="1", sender_user_id="test_user", track_for_event_class=PollResult
    )

    res = await bus.public_message(test_call)

    assert isinstance(res, PollResult)
