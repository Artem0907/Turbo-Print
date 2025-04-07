# Standard library imports
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod
from typing import TYPE_CHECKING
from typing import Any as _Any

# Local imports
from ._types import LogRecord as _LogRecord
from .filters import BaseFilter as _BaseFilter
from .formatters import BaseFormatter as _BaseFormatter

if TYPE_CHECKING:
    from ._turbo_print import TurboPrint


__all__ = ("BaseInnerMiddleware", "ContextMiddleware")


class BaseInnerMiddleware(_ABC):
    """Base class for all inner middleware handlers.

    Inner middleware handlers are used to process log records
    before they are processed by handlers. They can modify
        None = None
    the record, filter it, or perform other operations.
    """

    def __init__(
        self,
        priority: int = 0,
        formatter: _BaseFormatter | None = None,
        filters: list[_BaseFilter] | None = None,
    ) -> None:
        """Initialize the middleware handler.

        Args:
            priority: Priority of the middleware handler. Handlers with higher
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


class ContextMiddleware(BaseInnerMiddleware):
    """Middleware that adds context to log records."""

    def __init__(
        self,
        context: dict[str, _Any],
        priority: int = 0,
        formatter: _BaseFormatter | None = None,
        filters: list[_BaseFilter] | None = None,
    ) -> None:
        """Initialize the context middleware.

        Args:
            context: Dictionary of context to add to log records.
            priority: Priority of the middleware.
            formatter: Optional formatter for formatting log records.
            filters: Optional list of filters to apply to log records.
        """
        super().__init__(priority, formatter, filters)
        self.context = context

    async def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        """Add context to a log record.

        Args:
            logger: Logger instance that created the record.
            record: Log record to handle.
        """
        if not all([await filter.filter(record) for filter in self.filters]):
            return

        try:
            record["message"] = record["message"].format(**self.context)
        except (KeyError, ValueError) as e:
            # If formatting fails, log the error and keep the original message
            record["message"] = f"{record['message']} [Formatting error: {e!s}]"
