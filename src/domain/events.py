from dataclasses import dataclass

from src.domain.models import SimpleVote, SimplePoll


@dataclass
class Event:
    """
    Base class for events
    """


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
    results: dict[str, int]  # словарь вида вариант_айди:количество_ответов


@dataclass
class CreatePoll(Event):
    creator_id: str
    name: str
    description: str
    is_open: bool
    variants: list[str]  # варианты текстом в списке


@dataclass
class GetPollIds(Event):
    ...


@dataclass
class GetPollsByIds(Event):
    sender_user_id: str
    polls_ids: list[str]


@dataclass
class PollsIds(Event):
    ...


@dataclass
class Polls(Event):
    sender_user_id: str
    polls: list[SimplePoll]
