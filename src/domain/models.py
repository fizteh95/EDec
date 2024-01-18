from dataclasses import dataclass


class BaseDomainModel:
    """
    Base model class
    """


@dataclass
class User(BaseDomainModel):
    user_id: str
    name: str
    surname: str


@dataclass
class BasePoll(BaseDomainModel):
    poll_id: str
    creator_id: str
    name: str
    description: str
    is_open: bool
    ...


@dataclass
class SimpleVariant(BaseDomainModel):
    variant_id: str
    poll_id: str
    name: str


@dataclass
class SimplePoll(BasePoll):
    variants: list[SimpleVariant]


@dataclass
class SimpleVote(BaseDomainModel):
    user_id: str
    variant_id: str


@dataclass
class PollResultModel(BaseDomainModel):
    poll_id: str
    results: dict[str, int]  # словарь вида текст_варианта:количество_ответов
