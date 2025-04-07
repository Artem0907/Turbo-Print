# Standard library imports
from abc import ABC as _ABC
from abc import abstractmethod as _abstractmethod

# Local imports
from ._types import LogLevel as _LogLevel
from ._types import LogRecord as _LogRecord

__all__ = ("BaseFilter", "LevelFilter")


class BaseFilter(_ABC):
    """Base class for all log filters."""

    @_abstractmethod
    async def filter(self, record: _LogRecord) -> bool:
        """Filter a log record.

        Args:
            record: Log record to filter

        Returns:
            bool: True if the record should be processed, False otherwise
        """
        raise NotImplementedError()


class LevelFilter(BaseFilter):
    """Filter that filters log records based on their level."""

    def __init__(self, level: _LogLevel = _LogLevel.NOTSET) -> None:
        """Initialize the level filter.

        Args:
            level: Minimum level that passes through the filter.
        """
        super().__init__()
        self.level = level

    async def filter(self, record: _LogRecord) -> bool:
        """Filter a log record based on its level.

        Args:
            record: Log record to filter.

        Returns:
            bool: True if the record's level is greater than or equal to the filter's level.
        """  # noqa: E501
        return record["level"].value >= self.level.value
