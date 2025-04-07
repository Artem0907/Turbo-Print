from abc import ABC as _ABC, abstractmethod as _abstractmethod
from typing import TYPE_CHECKING, Optional as _Optional

from ._types import LogRecord as _LogRecord
from .formatters import BaseFormatter as _BaseFormatter
from .filters import BaseFilter as _BaseFilter

if TYPE_CHECKING:
    from ._turbo_print import TurboPrint


__all__ = ("BaseInnerMiddleware",)


class BaseInnerMiddleware(_ABC):
    """Base class for all inner middleware handlers.
    
    Inner middleware handlers are used to process log records before they are handled by handlers.
    They can modify the record, filter it, or perform other operations.
    """
    
    def __init__(
        self,
        priority: int = 0,
        formatter: _Optional[_BaseFormatter] = None,
        filters: _Optional[list[_BaseFilter]] = None,
    ) -> None:
        """Initialize the middleware handler.
        
        Args:
            priority: Priority of the middleware handler. Handlers with higher priority are executed first.
            formatter: Optional formatter to use when formatting log records.
            filters: Optional list of filters to apply to log records.
        """
        self.priority = priority
        self.formatter = formatter
        self.filters = filters or []

    @_abstractmethod
    async def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        """Process a log record.
        
        Args:
            logger: Logger instance that created the record.
            record: Log record to process.
            
        Raises:
            NotImplementedError: This method must be implemented in subclasses.
        """
        raise NotImplementedError()
