import copy

from src.domain.models import SimplePoll
from src.domain.models import SimpleVariant
from src.domain.models import SimpleVote
from src.domain.processors import AbstractAdapter


class FakeDbAdapter(AbstractAdapter):
    def __init__(self, initial: bool = False) -> None:
        self.polls: dict[str, SimplePoll] = {}
        self.votes: dict[str, SimpleVote] = {}
        self.variants: dict[str, SimpleVariant] = {}
        if initial:
            self.variants = {
                "1": SimpleVariant(name="Да", poll_id="1", variant_id="1"),
                "2": SimpleVariant(name="Нет", poll_id="1", variant_id="2"),
                "3": SimpleVariant(name="Да", poll_id="2", variant_id="3"),
                "4": SimpleVariant(name="Нет", poll_id="2", variant_id="4"),
                "5": SimpleVariant(name="Не знаю", poll_id="2", variant_id="5"),
            }
            self.polls = {
                "1": SimplePoll(
                    creator_id="1",
                    description="Описание самого первого опроса в системе",
                    poll_id="1",
                    is_open=True,
                    name="Первый опрос",
                    variants=[
                        SimpleVariant(name="Да", poll_id="1", variant_id="1"),
                        SimpleVariant(name="Нет", poll_id="1", variant_id="2"),
                    ],
                ),
                "2": SimplePoll(
                    creator_id="1",
                    description="Описание другого опроса, тоже нужное",
                    poll_id="2",
                    is_open=True,
                    name="Второй опрос",
                    variants=[
                        SimpleVariant(name="Да", poll_id="2", variant_id="3"),
                        SimpleVariant(name="Нет", poll_id="2", variant_id="4"),
                        SimpleVariant(name="Не знаю", poll_id="2", variant_id="5"),
                    ],
                )
            }

    async def create_poll(
        self,
        creator_id: str,
        name: str,
        description: str,
        is_open: bool,
        variants: list[str],
    ) -> SimplePoll:
        # create poll
        new_poll_id = f"{len(self.polls) + 1}"
        new_poll = SimplePoll(
            poll_id=new_poll_id,
            creator_id=creator_id,
            name=name,
            description=description,
            is_open=is_open,
            variants=[],
        )
        self.polls[new_poll_id] = new_poll

        # create variants
        for var in variants:
            new_variant_id = f"{len(self.variants) + 1}"
            new_variant = SimpleVariant(
                variant_id=new_variant_id, name=var, poll_id=new_poll_id
            )
            self.variants[new_variant_id] = new_variant
            new_poll.variants.append(new_variant)

        return new_poll

    async def get_polls_ids(self) -> list[str]:
        return list(self.polls.keys())

    async def get_polls(self, polls_ids: list[str]) -> list[SimplePoll]:
        result: list[SimplePoll] = []
        for poll_id in polls_ids:
            current_poll = copy.deepcopy(self.polls.get(poll_id))
            if not current_poll:
                continue
            for i in self.variants.values():
                if i.poll_id == poll_id:
                    current_poll.variants.append(i)
            result.append(current_poll)
        return result

    async def create_vote(self, user_id: str, poll_id: str, variant_id: str) -> bool:
        new_vote_id = f"{len(self.votes) + 1}"
        new_vote = SimpleVote(user_id=user_id, poll_id=poll_id, variant_id=variant_id)
        self.votes[new_vote_id] = new_vote
        return True

    async def get_poll_results(
        self, poll_id: str, sender_user_id: str
    ) -> dict[str, int]:
        res: dict[str, int] = {}
        poll = await self.get_polls(polls_ids=[poll_id])
        if not poll:
            return res
        for v in poll[0].variants:
            res[v.variant_id] = 0
            for p in self.votes.values():
                if p.variant_id == v.variant_id:
                    res[v.variant_id] += 1
        return res

    async def update_poll(self, poll_id: str, is_open: bool) -> bool:
        self.polls[poll_id].is_open = is_open
        return True
