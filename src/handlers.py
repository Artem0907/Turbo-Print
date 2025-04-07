from abc import ABC as _ABC, abstractmethod as _abstractmethod
from pathlib import Path as _Path
from typing import TYPE_CHECKING, Optional as _Optional, TextIO as _TextIO

from data import FileManager as _FileManager
from ._types import LogRecord as _LogRecord
from .formatters import BaseFormatter as _BaseFormatter
from .filters import BaseFilter as _BaseFilter


if TYPE_CHECKING:
    from ._turbo_print import TurboPrint


__all__ = ("BaseHandler", "StreamHandler", "FileHandler")


class BaseHandler(_ABC):
    def __init__(
        self,
        formatter: _Optional[_BaseFormatter] = None,
        filters: _Optional[list[_BaseFilter]] = None,
    ) -> None:
        self.formatter = formatter
        self.filters = filters or []

    @_abstractmethod
    async def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        """Process a log record.
        
        Args:
            logger: Logger instance that created the record.
            record: Log record to process.
        """
        raise NotImplementedError()


class StreamHandler(BaseHandler):
    def __init__(
        self,
        stdout: _Optional[_TextIO] = None,
        formatter: _Optional[_BaseFormatter] = None,
        filters: _Optional[list[_BaseFilter]] = None,
    ) -> None:
        super().__init__(formatter, filters)
        self.stdout = stdout

    async def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        if not all(filter.filter(record) for filter in self.filters):
            return
            
        stdout = self.stdout or logger.stdout
        formatter = self.formatter or logger.formatter

        stdout.write(formatter.colored_format(record) + "\n")
        stdout.flush()


class FileHandler(BaseHandler):
    def __init__(
        self,
        file_path: _Path,
        formatter: _Optional[_BaseFormatter] = None,
        filters: _Optional[list[_BaseFilter]] = None,
    ) -> None:
        super().__init__(formatter, filters)
        self.path = file_path
        self.manager = _FileManager()

    async def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        if not all(filter.filter(record) for filter in self.filters):
            return
            
        formatter = self.formatter or logger.formatter
        message = formatter.standard_format(record) + "\n"
        
        await self.manager.write(self.path, message)
