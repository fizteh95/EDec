from abc import ABC
from abc import abstractmethod

from src.domain.events import CreatePoll
from src.domain.events import Event
from src.domain.events import GetPollIds
from src.domain.events import GetPollResult
from src.domain.events import GetPollsByIds
from src.domain.events import PollResult
from src.domain.events import Polls
from src.domain.events import PollsIds
from src.domain.events import VoteEvent
from src.domain.models import SimplePoll
from src.domain.subscriber import Subscriber


class AbstractAdapter(ABC):
    @abstractmethod
    async def create_poll(
        self,
        creator_id: str,
        name: str,
        description: str,
        is_open: bool,
        variants: list[str],
    ) -> SimplePoll:
        raise NotImplementedError

    @abstractmethod
    async def get_polls(self, polls_ids: list[str]) -> list[SimplePoll]:
        raise NotImplementedError

    @abstractmethod
    async def get_polls_ids(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def create_vote(self, user_id: str, variant_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_poll_results(
        self, poll_id: str, sender_user_id: str
    ) -> dict[str, int]:
        raise NotImplementedError

    @abstractmethod
    async def update_poll(self, poll_id: str, is_open: bool) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def has_user_voted(self, user_id: str, poll_id: str) -> bool:
        raise NotImplementedError


class BaseProcessor(ABC, Subscriber):
    """
    Base processor class
    """

    def __init__(self, db_adapter: AbstractAdapter) -> None:
        self.db_adapter = db_adapter

    @staticmethod
    async def set_event_parent_id(parent_event: Event, child_event: Event) -> Event:
        if parent_event.parent_id:
            child_event.parent_id = parent_event.parent_id
        else:
            child_event.parent_id = parent_event.id_
        return child_event

    @abstractmethod
    async def process(self, event: Event) -> list[Event]:
        raise NotImplementedError


class VoteSaver(BaseProcessor):
    async def process(self, event: Event) -> list[Event]:
        if not isinstance(event, VoteEvent):
            return []
        _ = await self.db_adapter.create_vote(
            user_id=event.vote.user_id,
            variant_id=event.vote.variant_id,
        )
        return []


class PollSaver(BaseProcessor):
    async def process(self, event: Event) -> list[Event]:
        if not isinstance(event, CreatePoll):
            return []
        _ = await self.db_adapter.create_poll(
            creator_id=event.creator_id,
            name=event.name,
            description=event.description,
            is_open=event.is_open,
            variants=event.variants,
        )
        return []


class VoteCounter(BaseProcessor):
    async def process(self, event: Event) -> list[Event]:
        if not isinstance(event, GetPollResult):
            return []
        results: dict[str, int] = await self.db_adapter.get_poll_results(
            poll_id=event.poll_id, sender_user_id=event.sender_user_id
        )
        poll_result = PollResult(poll_id=event.poll_id, results=results)
        poll_result = await self.set_event_parent_id(event, poll_result)  # type: ignore
        return [poll_result]


class PollGetter(BaseProcessor):
    async def process(self, event: Event) -> list[Event]:
        if not isinstance(
            event,
            (
                GetPollIds,
                GetPollsByIds,
            ),
        ):
            return []
        if isinstance(event, GetPollsByIds):
            if len(event.polls_ids) == 1:
                user_has_voted = await self.db_adapter.has_user_voted(
                    user_id=event.sender_user_id, poll_id=event.polls_ids[0]
                )
                if user_has_voted:
                    out_event_voted = GetPollResult(
                        sender_user_id=event.sender_user_id, poll_id=event.polls_ids[0]
                    )
                    out_event_voted = await self.set_event_parent_id(event, out_event_voted)  # type: ignore
                    return [out_event_voted]
            polls = await self.db_adapter.get_polls(polls_ids=event.polls_ids)
            out_event = Polls(polls=polls, sender_user_id=event.sender_user_id)
            out_event = await self.set_event_parent_id(event, out_event)  # type: ignore
            return [out_event]
        elif isinstance(event, GetPollIds):
            ids = await self.db_adapter.get_polls_ids()
            out_ids_event = PollsIds(sender_user_id=event.sender_user_id, ids=ids)
            out_ids_event = await self.set_event_parent_id(event, out_ids_event)  # type: ignore
            return [out_ids_event]
        else:
            raise NotImplementedError
