from abc import ABC as _ABC, abstractmethod as _abstractmethod

from ._types import LogRecord as _LogRecord


__all__ = ("BaseFilter",)


class BaseFilter(_ABC):
    def __init__(self): ...
    @_abstractmethod
    def filter(self, record: _LogRecord) -> bool:
        """Filter a log record.
        
        Args:
            record: Log record to filter.
            
        Returns:
            bool: True if the record should be processed, False if it should be filtered out.
        """
        raise NotImplementedError()