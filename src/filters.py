from abc import ABC as _ABC, abstractmethod as _abstractmethod

from ._types import LogRecord as _LogRecord


__all__ = ("BaseFilter",)


class BaseFilter(_ABC):
    def __init__(self): ...
    @_abstractmethod
    def filter(self, record: _LogRecord) -> str:
        raise NotImplementedError()
