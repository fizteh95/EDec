import pytest

from src.domain.events import CreatePoll
from src.domain.events import GetPollResult
from src.domain.events import GetPollsByIds
from src.domain.events import PollResult
from src.domain.events import Polls
from src.domain.events import VoteEvent
from src.domain.models import SimpleVote
from src.domain.processors import AbstractAdapter
from src.domain.processors import PollGetter
from src.domain.processors import PollSaver
from src.domain.processors import VoteCounter
from src.domain.processors import VoteSaver
from src.services.message_bus import ConcreteMessageBus


@pytest.mark.asyncio
async def test_create_retrieve_poll(fake_db_adapter: AbstractAdapter) -> None:
    poll_saver = PollSaver(db_adapter=fake_db_adapter)
    poll_getter = PollGetter(db_adapter=fake_db_adapter)

    bus = ConcreteMessageBus()
    bus.register(poll_saver)
    bus.register(poll_getter)

    create_poll = CreatePoll(
        creator_id="test_user",
        name="test_poll",
        description="test poll for test",
        is_open=True,
        variants=["yes", "now"],
    )
    _ = await bus.public_message(create_poll)

    get_poll = GetPollsByIds(
        polls_ids=[list(fake_db_adapter.polls.keys())[0]],  # type: ignore
        sender_user_id="another_test_user",
        track_for_event_class=Polls,
    )
    res = await bus.public_message(get_poll)

    assert isinstance(res, Polls)
    assert res.polls[0].name == create_poll.name


@pytest.mark.asyncio
async def test_make_vote(fake_db_adapter: AbstractAdapter) -> None:
    poll_saver = PollSaver(db_adapter=fake_db_adapter)
    poll_getter = PollGetter(db_adapter=fake_db_adapter)
    vote_counter = VoteCounter(db_adapter=fake_db_adapter)
    vote_saver = VoteSaver(db_adapter=fake_db_adapter)

    bus = ConcreteMessageBus()
    bus.register(poll_saver)
    bus.register(poll_getter)
    bus.register(vote_counter)
    bus.register(vote_saver)

    create_poll = CreatePoll(
        creator_id="test_user",
        name="test_poll",
        description="test poll for test",
        is_open=True,
        variants=["yes", "no"],
    )
    _ = await bus.public_message(create_poll)

    get_poll = GetPollsByIds(
        polls_ids=[list(fake_db_adapter.polls.keys())[0]],  # type: ignore
        sender_user_id="another_test_user",
        track_for_event_class=Polls,
    )
    res = await bus.public_message(get_poll)
    created_poll: SimplePoll = res.polls[0]  # type: ignore

    create_vote = VoteEvent(
        vote=SimpleVote(
            poll_id=created_poll.poll_id,
            user_id="test_user",
            variant_id=created_poll.variants[0].variant_id,
        )
    )
    _ = await bus.public_message(create_vote)

    get_result = GetPollResult(
        poll_id=created_poll.poll_id,
        sender_user_id="test_user",
        track_for_event_class=PollResult,
    )
    res = await bus.public_message(get_result)

    assert isinstance(res, PollResult)
    assert res.poll_id == created_poll.poll_id
    assert res.results == {"1": 1, "2": 0}
