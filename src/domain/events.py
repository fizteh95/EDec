import typing as tp
import uuid
from dataclasses import dataclass

from src.domain.models import SimplePoll
from src.domain.models import SimpleVote


@dataclass(kw_only=True)
class Event:
    """
    Base class for events
    """

    id_: str = ""
    parent_id: str = ""
    track_for_event_class: list[type] | None = None

    def __post_init__(self) -> None:
        self.id_ = str(uuid.uuid4())


@dataclass
class VoteEvent(Event):
    vote: SimpleVote


@dataclass
class GetPollResult(Event):
    sender_user_id: str
    poll_id: str


@dataclass
class PollResult(Event):
    poll_id: str
    results: dict[str, int]  # словарь вида вариант_имя:количество_ответов


@dataclass
class CreatePoll(Event):
    creator_id: str
    name: str
    description: str
    is_open: bool
    variants: list[str]  # варианты текстом в списке


@dataclass
class GetPollIds(Event):
    sender_user_id: str
    ...


@dataclass
class GetPollsByIds(Event):
    sender_user_id: str
    polls_ids: list[str]


@dataclass
class PollsIds(Event):
    sender_user_id: str
    ids: list[str]


@dataclass
class Polls(Event):
    sender_user_id: str
    polls: list[SimplePoll]
