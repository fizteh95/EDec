from abc import ABC
from abc import abstractmethod

from src.domain.events import Event
from src.domain.subscriber import Subscriber


class MessageBus(ABC):
    @abstractmethod
    def __init__(self) -> None:
        """Initialize of bus"""

    @abstractmethod
    def register(self, subscriber: Subscriber) -> None:
        """Register subscriber in bus"""

    @abstractmethod
    def unregister(self, subscriber: Subscriber) -> None:
        """Unregister subscriber in bus"""

    @abstractmethod
    async def public_message(self, message: Event | list[Event]) -> None | Event:
        """Public message in bus for all subscribers"""


class ConcreteMessageBus(MessageBus):
    def __init__(self) -> None:
        """Initialize of bus"""
        self.queue: list[Event] = []
        self.services: list[Subscriber] = []

    def register(self, subscriber: Subscriber) -> None:
        """Register subscriber in bus"""
        self.services.append(subscriber)

    def unregister(self, subscriber: Subscriber) -> None:
        """Unregister subscriber in bus"""
        self.services.remove(subscriber)

    async def public_message(self, message: Event | list[Event]) -> None | Event:
        """Public and handle message"""
        track_for_class = None
        track_for_id = None
        return_event = None
        if isinstance(message, list):
            self.queue += message
        elif isinstance(message, Event):
            self.queue.append(message)
            if message.track_for_event_class:
                track_for_class = message.track_for_event_class
                track_for_id = message.id_
        while self.queue:
            current_message = self.queue.pop(0)
            if (
                track_for_id
                and track_for_class
                and not return_event
                and current_message.__class__ == track_for_class
                and current_message.parent_id == track_for_id
            ):
                return_event = current_message
            for sub in self.services:
                events = await sub.process(current_message)
                self.queue += events
        return return_event
