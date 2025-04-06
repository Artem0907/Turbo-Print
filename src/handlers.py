from abc import ABC as _ABC, abstractmethod as _abstractmethod
from typing import TYPE_CHECKING, Optional as _Optional, TextIO as _TextIO

from ._types import LogRecord as _LogRecord
from .formatters import BaseFormatter as _BaseFormatter
from .filters import BaseFilter as _BaseFilter

if TYPE_CHECKING:
    from ._turbo_print import TurboPrint


__all__ = ("BaseHandler",)


class BaseHandler(_ABC):
    def __init__(
        self,
        formatter: _Optional[_BaseFormatter] = None,
        filters: _Optional[list[_BaseFilter]] = None,
    ):
        self.formatter = formatter
        self.filters = filters or []

    @_abstractmethod
    def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        raise NotImplementedError()


class StreamHandler(BaseHandler):
    def __init__(
        self,
        stdout: _Optional[_TextIO] = None,
        formatter: _Optional[_BaseFormatter] = None,
        filters: _Optional[list[_BaseFilter]] = None,
    ):
        super().__init__(formatter, filters)
        self.stdout = stdout

    def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        if not all(map(lambda filter: filter.filter(record), self.filters)):
            return
        stdout = self.stdout or logger.stdout
        formatter = self.formatter or logger.formatter

        stdout.write(formatter.colored_format(record) + "\n")
        stdout.flush()
