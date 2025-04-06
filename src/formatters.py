from abc import ABC as _ABC, abstractmethod as _abstractmethod

from colorama import Style as _Style

from ._types import LogRecord as _LogRecord


__all__ = ("BaseFormatter", "DefaultFormatter")


class BaseFormatter(_ABC):
    def __init__(self): ...
    @_abstractmethod
    def standard_format(self, record: _LogRecord) -> str:
        raise NotImplementedError()

    @_abstractmethod
    def colored_format(self, record: _LogRecord) -> str:
        raise NotImplementedError()


class DefaultFormatter(BaseFormatter):
    def __init__(
        self,
        format: str = "[{datetime:%d/%m/%Y %H:%M:%S}] {logger.prefix} | {level.name}[{level.value}]: {message}",
    ):
        super().__init__()
        self.format = format

    def standard_format(self, record: _LogRecord) -> str:
        new_record = record.copy()
        new_record["logger"].prefix = (
            new_record["logger"].prefix or new_record["logger"].name
        )
        return self.format.format(**new_record)

    def colored_format(self, record: _LogRecord) -> str:
        return record["level"].color + self.standard_format(record) + _Style.RESET_ALL
