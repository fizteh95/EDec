import asyncio
import typing as tp

from src.domain.processors import PollGetter
from src.domain.processors import PollSaver
from src.domain.processors import VoteCounter
from src.domain.processors import VoteSaver
from src.services.db_adapter import FakeDbAdapter
from src.services.message_bus import MessageBus
from src.web.web import AbstractWeb
from src.web.web_adapter import AbstractWebAdapter


async def bootstrap(
    bus: tp.Type[MessageBus],
    web: tp.Type[AbstractWeb],
    web_adapter: tp.Type[AbstractWebAdapter],
) -> tp.Any:
    # if migrator:
    #     await migrator().run_async_upgrade()

    fake_db_adapter = FakeDbAdapter(initial=True)

    poll_saver = PollSaver(db_adapter=fake_db_adapter)
    poll_getter = PollGetter(db_adapter=fake_db_adapter)
    vote_counter = VoteCounter(db_adapter=fake_db_adapter)
    vote_saver = VoteSaver(db_adapter=fake_db_adapter)

    concrete_bus = bus()

    concrete_bus.register(poll_saver)
    concrete_bus.register(poll_getter)
    concrete_bus.register(vote_counter)
    concrete_bus.register(vote_saver)
    # mp = metrics_processor()
    # concrete_bus.register(mp)

    concrete_web_adapter = web_adapter(
        bus=concrete_bus,
        # metrics_processor=mp,
    )
    concrete_web = web(
        host="localhost",
        port=8080,
        adapter=concrete_web_adapter,
        message_handler=concrete_web_adapter.message_handler,
        # metrics_handler=concrete_web_adapter.get_metrics,
    )

    # if poller is not None and poller_adapter is not None:
    #     return asyncio.gather(concrete_poller.poll(), concrete_web.start())
    # else:
    return asyncio.gather(concrete_web.start())
