from abc import ABC as _ABC, abstractmethod as _abstractmethod

from src.types import LogRecord as _LogRecord

__all__ = ["BaseFilter"]


class BaseFilter(_ABC):
    """Базовый класс для фильтрации записей лога"""

    @_abstractmethod
    def filter(self, record: _LogRecord) -> bool:
        """Фильтрация записи"""
        pass
