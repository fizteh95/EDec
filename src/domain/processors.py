from abc import ABC
from abc import abstractmethod

from src.domain.events import CreatePoll
from src.domain.events import Event
from src.domain.events import GetPollResult
from src.domain.events import PollResult
from src.domain.events import VoteEvent
from src.domain.models import SimplePoll
from src.domain.models import SimpleVote
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
    async def create_vote(self, vote: SimpleVote) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_poll_results(
        self, poll_id: str, sender_user_id: str
    ) -> dict[str, int]:
        raise NotImplementedError

    @abstractmethod
    async def update_poll(self, poll_id: str, is_open: bool) -> bool:
        raise NotImplementedError


class BaseProcessor(ABC, Subscriber):
    """
    Base processor class
    """

    def __init__(self, db_adapter: AbstractAdapter) -> None:
        self.db_adapter = db_adapter

    @abstractmethod
    async def process(self, event: Event) -> list[Event]:
        raise NotImplementedError


class VoteSaver(BaseProcessor):
    async def process(self, event: Event) -> list[Event]:
        if not isinstance(event, VoteEvent):
            return []
        _ = await self.db_adapter.create_vote(vote=event.vote)
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
        poll_result.parent_id = event.id_
        return [poll_result]
