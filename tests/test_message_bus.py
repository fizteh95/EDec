import asyncio
import time
from dataclasses import dataclass

import pytest

from src.domain.events import Event
from src.domain.events import GetPollResult
from src.domain.events import PollResult
from src.domain.processors import AbstractAdapter
from src.domain.processors import BaseProcessor
from src.domain.processors import VoteCounter
from src.services.message_bus import ConcreteMessageBus
from src.services.message_bus import MessageBus


@pytest.mark.asyncio
async def test_message_bus_returning(fake_db_adapter: AbstractAdapter) -> None:
    vote_counter = VoteCounter(db_adapter=fake_db_adapter)

    bus = ConcreteMessageBus()
    bus.register(vote_counter)

    test_call = GetPollResult(
        poll_id="1", sender_user_id="test_user", track_for_event_class=[PollResult]
    )

    res = await bus.public_message(test_call)

    assert isinstance(res, PollResult)


# будет ли бесконечно крутиться вызов .public_message если будут прилетать новые сообщения
@pytest.mark.asyncio
async def test_message_bus_for_infinite(fake_db_adapter: AbstractAdapter) -> None:
    @dataclass
    class TestEvent(Event):
        wait_for: int | float

    class TestClass(BaseProcessor):
        async def process(self, event: Event) -> list[Event]:
            if not isinstance(event, TestEvent):
                return []
            await asyncio.sleep(event.wait_for)
            return []

    vote_counter = VoteCounter(db_adapter=fake_db_adapter)
    sleep_processor = TestClass(db_adapter=fake_db_adapter)

    async def delayed_bus_call(internal_bus: MessageBus) -> None:
        await asyncio.sleep(0.5)
        wait_event = TestEvent(wait_for=0.5)
        await internal_bus.public_message(message=wait_event)
        return None

    async def normal_bus_call(internal_bus: MessageBus) -> Event:
        start_time = time.time()
        wait_event = TestEvent(wait_for=1.5)
        probe_event = GetPollResult(
            poll_id="1", sender_user_id="test_user", track_for_event_class=[PollResult]
        )
        result = await internal_bus.public_message(message=[probe_event, wait_event])
        if result is None:
            raise
        result.execute_time = time.time() - start_time  # type: ignore
        return result

    bus = ConcreteMessageBus()
    bus.register(vote_counter)
    bus.register(sleep_processor)

    res = await asyncio.gather(
        delayed_bus_call(internal_bus=bus),
        normal_bus_call(internal_bus=bus)
    )

    assert len(res) == 2
    for item in res:
        if item is None:
            continue
        assert isinstance(item, PollResult)
        assert item.execute_time < 1.6  # type: ignore
        break
    else:
        raise
