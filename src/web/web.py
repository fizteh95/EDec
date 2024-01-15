import json
import typing as tp
from abc import ABC
from abc import abstractmethod

import uvicorn
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Request
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
        self.router = APIRouter()
        self.router.add_api_route(
            path="/healthcheck", endpoint=self.healthcheck, methods=["GET", "POST"]
        )
        self.router.add_api_route(
            path="/polls", endpoint=self.get_polls, methods=["GET"]
        )
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
        response: _TemplateResponse = await self.adapter.get_polls(request=request)
        return response

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
