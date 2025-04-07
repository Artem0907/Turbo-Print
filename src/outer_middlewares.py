# Standard library imports
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod
from typing import TYPE_CHECKING

# Local imports
from ._types import LogLevel as _LogLevel
from ._types import LogRecord as _LogRecord
from .filters import BaseFilter as _BaseFilter
from .formatters import BaseFormatter as _BaseFormatter

if TYPE_CHECKING:
    from ._turbo_print import TurboPrint


__all__ = ("BaseOuterMiddleware", "ErrorHandlerMiddleware")


class BaseOuterMiddleware(_ABC):
    """Base class for all outer middleware.

    Outer middleware are used to process log records after they
    have been processed by handlers. They can modify the record,
    filter it, or perform other operations.
    """

    def __init__(
        self,
        priority: int = 0,
        formatter: _BaseFormatter | None = None,
        filters: list[_BaseFilter] | None = None,
    ) -> None:
        """Initialize the middleware.

        Args:
            priority: Priority of the middleware. Middleware with higher
                     priority are executed first.
            formatter: Optional formatter for formatting log records.
            filters: Optional list of filters to apply to log records.
        """
        self.priority = priority
        self.formatter = formatter
        self.filters = filters or []

    @_abstractmethod
    async def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        """Handle a log record.

        Args:
            logger: Logger instance that created the record.
            record: Log record to handle.

        Raises:
            NotImplementedError: This method must be implemented in subclasses.
        """
        raise NotImplementedError()


class ErrorHandlerMiddleware(BaseOuterMiddleware):
    """Middleware for handling errors in log records."""

    def __init__(
        self,
        priority: int = 0,
        formatter: _BaseFormatter | None = None,
        filters: list[_BaseFilter] | None = None,
    ) -> None:
        """Initialize the error handler middleware.

        Args:
            priority: Priority of the middleware.
            formatter: Optional formatter for formatting log records.
            filters: Optional list of filters to apply to log records.
        """
        super().__init__(priority, formatter, filters)

    async def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        """Handle errors in a log record.

        Args:
            logger: Logger instance that created the record.
            record: Log record to handle.
        """
        if not all([await filter.filter(record) for filter in self.filters]):
            return

        if record["level"] >= _LogLevel.ERROR:
            # Here you can add additional error handling logic
            # For example, sending notifications, creating tickets, etc.
            # For example, just log additional information
            error_message = f"Error occurred: {record['message']}"
            await logger.alog(error_message, level=_LogLevel.ERROR)
