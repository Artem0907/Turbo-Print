# Standard library imports
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod

# Local imports
from ._types import LogRecord as _LogRecord

__all__ = ("BaseFormatter", "DefaultFormatter")


class BaseFormatter(_ABC):
    """Base class for all log formatters."""

    @_abstractmethod
    async def standard_format(self, record: _LogRecord) -> str:
        """Format log record in standard format.

        Args:
            record: Log record to format

        Returns:
            str: Formatted string
        """
        raise NotImplementedError()

    @_abstractmethod
    async def colored_format(self, record: _LogRecord) -> str:
        """Format log record with color highlighting.

        Args:
            record: Log record to format

        Returns:
            str: Formatted string with color highlighting
        """
        raise NotImplementedError()


class DefaultFormatter(BaseFormatter):
    """Default formatter for logs."""

    def __init__(self, format_string: str | None = None) -> None:
        """Initialize the formatter.

        Args:
            format_string: Format string for logs
        """
        self.format_string = (
            format_string
            or "[{datetime:%d/%m/%Y %H:%M:%S}] {logger.prefix} | {level.name}[{level.value}]: {message}"
        )

    async def standard_format(self, record: _LogRecord) -> str:
        """Format log record in standard format.

        Args:
            record: Log record to format

        Returns:
            str: Formatted string
        """
        return self.format_string.format(
            logger=record["logger"],
            datetime=record["datetime"],
            level=record["level"],
            message=record["message"],
        )

    async def colored_format(self, record: _LogRecord) -> str:
        """Format log record with color highlighting.

        Args:
            record: Log record to format

        Returns:
            str: Formatted string with color highlighting
        """
        level_color = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
        }.get(
            record["level"].name, "\033[0m"
        )  # Default to reset

        reset_color = "\033[0m"
        formatted_message = await self.standard_format(record)
        return f"{level_color}{formatted_message}{reset_color}"
