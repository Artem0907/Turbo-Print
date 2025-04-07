# Standard library imports
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod
from pathlib import Path as _Path
from typing import TYPE_CHECKING
from typing import TextIO as _TextIO

# Third-party imports
from data import FileManager as _FileManager

# Local imports
from ._types import LogLevel as _LogLevel
from ._types import LogRecord as _LogRecord
from .filters import BaseFilter as _BaseFilter
from .formatters import BaseFormatter as _BaseFormatter

if TYPE_CHECKING:
    from ._turbo_print import TurboPrint


__all__ = ("BaseHandler", "FileHandler", "StreamHandler")


class BaseHandler(_ABC):
    """Base class for all log handlers."""

    def __init__(
        self,
        formatter: _BaseFormatter | None = None,
        filters: list[_BaseFilter] | None = None,
    ) -> None:
        """Initialize the handler.

        Args:
            formatter: Formatter for messages
            filters: List of filters
        """
        self.formatter = formatter
        self.filters = filters or []

    @_abstractmethod
    async def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        """Handle a log record.

        Args:
            logger: Logger instance that created the record
            record: Log record to handle
        """
        raise NotImplementedError()


class StreamHandler(BaseHandler):
    """Handler for outputting logs to a stream."""

    def __init__(
        self,
        stdout: _TextIO | None = None,
        formatter: _BaseFormatter | None = None,
        filters: list[_BaseFilter] | None = None,
    ) -> None:
        """Initialize the stream handler.

        Args:
            stdout: Output stream
            formatter: Formatter for messages
            filters: List of filters
        """
        super().__init__(formatter, filters)
        self.stdout = stdout

    async def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        """Handle a log record with output to stream.

        Args:
            logger: Logger instance
            record: Log record to handle
        """
        if not all([await filter.filter(record) for filter in self.filters]):
            return

        stdout = self.stdout or logger.stdout
        formatter = self.formatter or logger.formatter

        formatted_message = await formatter.colored_format(record)
        stdout.write(formatted_message + "\n")
        await logger.async_loop.run_in_executor(None, stdout.flush)


class FileHandler(BaseHandler):
    """Handler for writing logs to a file."""

    def __init__(
        self,
        file_path: _Path,
        formatter: _BaseFormatter | None = None,
        filters: list[_BaseFilter] | None = None,
    ) -> None:
        """Initialize the file handler.

        Args:
            file_path: Path to the file for writing
            formatter: Formatter for messages
            filters: List of filters
        """
        super().__init__(formatter, filters)
        self.manager = _FileManager(file_path)

    async def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        """Handle a log record with writing to file.

        Args:
            logger: Logger instance
            record: Log record to handle
        """
        if not all([await filter.filter(record) for filter in self.filters]):
            return

        formatter = self.formatter or logger.formatter
        message = await formatter.standard_format(record) + "\n"

        try:
            await self.manager.write(self.manager.get_path(), message)
        except Exception as e:
            # Log the error but don't let it propagate
            error_message = (
                f"Error writing to file {self.manager.get_path()}: {e!s}"
            )
            await logger.alog(error_message, level=_LogLevel.ERROR)
