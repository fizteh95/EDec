import json
import typing as tp
from abc import ABC
from abc import abstractmethod

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from src.domain.events import CreatePoll
from src.domain.events import GetPollIds
from src.domain.events import GetPollsByIds
from src.domain.events import Polls
from src.domain.events import PollsIds
from src.domain.events import VoteEvent
from src.domain.models import SimpleVote
from src.services.message_bus import MessageBus


class AbstractWebAdapter(ABC):
    def __init__(
        self,
        # uow: tp.Type[AbstractUOWFactory],
        # ctx_repo: AbstractContextRepo,
        bus: MessageBus,
        # metrics_processor: AbstractMetricsProcessor,
    ) -> None:
        # self.uow = uow
        # self.ctx_repo = ctx_repo
        self.bus = bus
        # self.metrics_processor = metrics_processor

    @abstractmethod
    async def message_handler(
        self, unparsed_event: dict[str, tp.Any]
    ) -> dict[str, tp.Any]:
        """Process income message"""

    @abstractmethod
    async def get_metrics(self) -> tuple[tp.Any, bytes]:
        """Get collected prometheus metrics"""

    @abstractmethod
    async def get_polls(self, request: Request) -> _TemplateResponse:
        """Return polls list"""

    @abstractmethod
    async def new_poll(self, request: Request) -> _TemplateResponse:
        """Return page to create poll"""

    @abstractmethod
    async def create_new_poll(
        self, poll_name: str, poll_description: str, variants: list[str]
    ) -> bool:
        """Create poll from form"""

    @abstractmethod
    async def poll_vote(self, request: Request, item_id: str) -> _TemplateResponse:
        """Page for vote in poll"""

    @abstractmethod
    async def create_vote(self, variant_id: str) -> bool:
        """Create vote in poll"""


class WebAdapter(AbstractWebAdapter):
    def __init__(
        self,
        # uow: tp.Type[AbstractUOWFactory],
        # ctx_repo: AbstractContextRepo,
        bus: MessageBus,
        # metrics_processor: AbstractMetricsProcessor,
    ) -> None:
        super().__init__(
            # uow=uow,
            # ctx_repo=ctx_repo,
            bus=bus,
            # metrics_processor=metrics_processor,
        )
        self.templates = Jinja2Templates(directory="templates")

    async def get_metrics(self) -> tuple[tp.Any, bytes]:
        # return await self.metrics_processor.get_metrics()
        return 1, b"0"

    # @staticmethod
    # def _get_headers(headers: tp.List[tp.List[str]]) -> tp.Dict[str, str]:
    #     return {header: value for header, value in headers}
    #

    async def get_polls(self, request: Request) -> _TemplateResponse:
        """Return polls list"""
        polls_ids_request = GetPollIds(
            sender_user_id="", track_for_event_class=PollsIds
        )
        polls_ids: PollsIds = await self.bus.public_message(message=polls_ids_request)  # type: ignore

        get_poll_request = GetPollsByIds(
            polls_ids=polls_ids.ids,
            sender_user_id="",
            track_for_event_class=Polls,
        )
        res: Polls = await self.bus.public_message(get_poll_request)  # type: ignore
        return self.templates.TemplateResponse(
            "all/polls.html", {"request": request, "polls": res.polls}
        )

    async def new_poll(self, request: Request) -> _TemplateResponse:
        return self.templates.TemplateResponse(
            "all/new_poll.html", {"request": request}
        )

    async def create_new_poll(
        self, poll_name: str, poll_description: str, variants: list[str]
    ) -> bool:
        """Create poll from form"""
        create_poll = CreatePoll(
            creator_id="",
            name=poll_name,
            description=poll_description,
            is_open=True,
            variants=variants,
        )
        _ = await self.bus.public_message(create_poll)
        return True

    async def poll_vote(self, request: Request, item_id: str) -> _TemplateResponse:
        get_poll_request = GetPollsByIds(
            polls_ids=[str(item_id)],
            sender_user_id="",
            track_for_event_class=Polls,
        )
        res: Polls = await self.bus.public_message(get_poll_request)  # type: ignore

        poll = res.polls[0]

        return self.templates.TemplateResponse(
            "all/poll_vote.html", {"request": request, "poll": poll}
        )

    async def create_vote(self, variant_id: str) -> bool:
        """Create vote in poll"""
        create_vote = VoteEvent(
            vote=SimpleVote(
                user_id="",
                variant_id=variant_id,
            )
        )
        _ = await self.bus.public_message(create_vote)
        return True

    async def message_handler(
        self, unparsed_event: tp.Dict[str, tp.Any]
    ) -> tp.Dict[str, tp.Any]:
        transformed_events = {"user_id": "t", "events": "t"}
        return transformed_events
