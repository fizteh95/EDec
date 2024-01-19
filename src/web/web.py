import json
import typing as tp
import uuid
from abc import ABC
from abc import abstractmethod

import uvicorn
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Request
from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.templating import _TemplateResponse

from src.web.web_adapter import AbstractWebAdapter


class AbstractWeb(ABC):
    """
    Base class for web implementation
    """

    def __init__(
        self,
        host: str,
        port: int,
        adapter: AbstractWebAdapter,
        message_handler: tp.Callable[
            [dict[str, tp.Any]], tp.Awaitable[dict[str, tp.Any]]
        ],
        # metrics_handler: tp.Callable[[None], tp.Awaitable[tuple[tp.Any, bytes]]],
    ) -> None:
        self.host = host
        self.port = port
        self.adapter = adapter
        self.message_handler = message_handler

    @abstractmethod
    async def start(self) -> None:
        raise NotImplementedError


class CookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        edec_user_token = request.cookies.get("X-edec-poll")
        if not edec_user_token:
            edec_user_token = str(uuid.uuid4())
        request.state.user_id = edec_user_token
        # if request.url.path not in ["/healthcheck", "/metrics"]:
        #     logger.info(f"API request {request.method} {request.url.path}")
        response = await call_next(request)
        response.set_cookie(key="X-edec-poll", value=edec_user_token)
        return response


class FastApiWeb(AbstractWeb):
    def __init__(
        self,
        host: str,
        port: int,
        adapter: AbstractWebAdapter,
        message_handler: tp.Callable[
            [dict[str, tp.Any]], tp.Awaitable[dict[str, tp.Any]]
        ],
        # metrics_handler: tp.Callable[[None], tp.Awaitable[tuple[tp.Any, bytes]]],
    ) -> None:
        super().__init__(
            host=host, port=port, message_handler=message_handler, adapter=adapter
        )
        self.app = FastAPI()
        self.app.add_middleware(CookieMiddleware)
        self.router = APIRouter()
        self.router.add_api_route(
            path="/healthcheck", endpoint=self.healthcheck, methods=["GET", "POST"]
        )
        self.router.add_api_route(
            path="/polls", endpoint=self.get_polls, methods=["GET"]
        )
        self.router.add_api_route(
            path="/new_poll", endpoint=self.new_poll, methods=["GET"]
        )
        self.router.add_api_route(
            path="/create_new_poll", endpoint=self.create_new_poll, methods=["POST"]
        )
        self.router.add_api_route(
            path="/poll_vote/{item_id}", endpoint=self.poll_vote, methods=["GET"]
        )
        self.router.add_api_route(path="/vote", endpoint=self.vote, methods=["POST"])
        # self.router.add_api_route(
        #     path="/metrics", endpoint=self.metrics, methods=["GET"]
        # )
        # self.router.add_api_route(
        #     path="/message_text", endpoint=self.message_handler, methods=["POST"]
        # )
        self.app.include_router(self.router)

    @staticmethod
    async def healthcheck() -> dict[str, str]:
        print("hhhh")
        return {"status": "ok"}

    async def get_polls(self, request: Request) -> _TemplateResponse:
        user_id = request.state.user_id
        response: _TemplateResponse = await self.adapter.get_polls(
            request=request, user_id=user_id
        )
        return response

    async def new_poll(self, request: Request) -> _TemplateResponse:
        response: _TemplateResponse = await self.adapter.new_poll(request=request)
        return response

    async def create_new_poll(self, request: Request) -> RedirectResponse:
        da = await request.form()
        da = jsonable_encoder(da)
        poll_name = da.get("poll_name")
        poll_description = da.get("poll_description")
        variants: list[str] = [
            value
            for key, value in da.items()
            if (key not in ["poll_name", "poll_description"])
            and (isinstance(value, str))
        ]
        if (
            not (poll_name and isinstance(poll_name, str))
            or not (poll_description and isinstance(poll_description, str))
            or not (
                variants
                and isinstance(variants, list)
                and all(isinstance(item, str) for item in variants)
            )
        ):
            raise
        user_id = request.state.user_id
        _ = await self.adapter.create_new_poll(
            poll_name=poll_name,
            poll_description=poll_description,
            variants=variants,
            user_id=user_id,
        )
        return RedirectResponse("/polls", status_code=status.HTTP_302_FOUND)

    async def poll_vote(self, request: Request, item_id: str) -> _TemplateResponse:
        user_id = request.state.user_id
        response: _TemplateResponse = await self.adapter.poll_vote(
            request=request, item_id=item_id, user_id=user_id
        )
        return response

    async def vote(self, request: Request) -> RedirectResponse:
        da = await request.form()
        da = jsonable_encoder(da)
        variant_id = da.get("radio")
        if (not variant_id) or (not isinstance(variant_id, str)):
            raise
        user_id = request.state.user_id
        referer_id = request.headers.get("Referer")
        if not referer_id:
            _ = await self.adapter.create_vote(variant_id=variant_id, user_id=user_id)
            return RedirectResponse("/polls", status_code=status.HTTP_302_FOUND)
        poll_id = referer_id.split("/")[-1]
        _ = await self.adapter.create_vote(variant_id=variant_id, user_id=user_id)
        return RedirectResponse(
            f"/poll_vote/{poll_id}", status_code=status.HTTP_302_FOUND
        )

    @staticmethod
    def configure_uvicorn_logger() -> dict[str, str]:
        log_config = uvicorn.config.LOGGING_CONFIG
        log_format = json.dumps(
            {
                "datetime": "%(asctime)s.%(msecs)03d",
                "loglevel": "%(levelname)-4s",
                "message": "%(message)s",
            }
        )
        log_config["formatters"]["default"]["fmt"] = log_format
        log_config["formatters"]["default"]["datefmt"] = "%Y-%m-%dT%H:%M:%S"
        del log_config["formatters"]["default"]["use_colors"]
        return log_config

    async def start(self) -> None:
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=int(self.port),
            log_config=self.configure_uvicorn_logger(),
            access_log=False,
        )
        server = uvicorn.Server(config)
        await server.serve()
