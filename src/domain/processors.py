from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    """
    Base processor class
    """
    async def process(self):
        ...
