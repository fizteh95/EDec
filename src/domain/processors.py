from abc import ABC, abstractmethod

from src.domain.models import SimplePoll, SimpleVote


class AbstractAdapter(ABC):
    @abstractmethod
    async def create_poll(self, creator_id: str, name: str, description: str, is_open: bool, variants: list[str]) -> SimplePoll:
        raise NotImplementedError

    @abstractmethod
    async def get_polls(self, polls_ids: list[str]) -> list[SimplePoll]:
        raise NotImplementedError

    @abstractmethod
    async def create_vote(self, vote: SimpleVote) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def get_poll_results(self, poll_id: str, sender_user_id: str) -> dict[str, int]:
        raise NotImplementedError

    @abstractmethod
    async def update_poll(self, poll_id: str, is_open: bool) -> bool:
        raise NotImplementedError


class BaseProcessor(ABC):
    """
    Base processor class
    """
    def __init__(self):
        ...

    async def process(self):
        ...
