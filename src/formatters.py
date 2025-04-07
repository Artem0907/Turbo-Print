from abc import ABC as _ABC, abstractmethod as _abstractmethod
from typing import ClassVar as _ClassVar

from colorama import Style as _Style

from ._types import LogRecord as _LogRecord


__all__ = ("BaseFormatter", "DefaultFormatter")


class BaseFormatter(_ABC):
    """Base class for all formatters."""
    
    def __init__(self) -> None:
        """Initialize the formatter."""
        super().__init__()

    @_abstractmethod
    def standard_format(self, record: _LogRecord) -> str:
        """Format a log record without colors.
        
        Args:
            record: Log record to format.
            
        Returns:
            str: Formatted log message.
        """
        raise NotImplementedError()

    @_abstractmethod
    def colored_format(self, record: _LogRecord) -> str:
        """Format a log record with colors.
        
        Args:
            record: Log record to format.
            
        Returns:
            str: Formatted and colored log message.
        """
        raise NotImplementedError()


class DefaultFormatter(BaseFormatter):
    """Default formatter implementation."""
    
    DEFAULT_FORMAT: _ClassVar[str] = "[{datetime:%d/%m/%Y %H:%M:%S}] {logger.prefix} | {level.name}[{level.value}]: {message}"

    def __init__(self, format: str = DEFAULT_FORMAT) -> None:
        """Initialize the default formatter.
        
        Args:
            format: Format string to use when formatting log records.
        """
        super().__init__()
        self._format = format

    def standard_format(self, record: _LogRecord) -> str:
        """Format a log record without colors.
        
        Args:
            record: Log record to format.
            
        Returns:
            str: Formatted log message.
        """
        logger = record["logger"]
        prefix = logger.prefix or logger.name
        return self._format.format(
            datetime=record["datetime"],
            logger=logger,
            level=record["level"],
            message=record["message"],
            prefix=prefix
        )

    def colored_format(self, record: _LogRecord) -> str:
        """Format a log record with colors.
        
        Args:
            record: Log record to format.
            
        Returns:
            str: Formatted and colored log message.
        """
        return f"{record['level'].color}{self.standard_format(record)}{_Style.RESET_ALL}"
