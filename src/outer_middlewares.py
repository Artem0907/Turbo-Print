from abc import ABC as _ABC, abstractmethod as _abstractmethod
from typing import TYPE_CHECKING, Optional as _Optional

from ._types import LogRecord as _LogRecord
from .formatters import BaseFormatter as _BaseFormatter
from .filters import BaseFilter as _BaseFilter

if TYPE_CHECKING:
    from ._turbo_print import TurboPrint


__all__ = ("BaseOuterMiddleware",)


class BaseOuterMiddleware(_ABC):
    def __init__(
        self,
        priority: int = 0,
        formatter: _Optional[_BaseFormatter] = None,
        filters: _Optional[list[_BaseFilter]] = None,
    ):
        self.priority = priority
        self.formatter = formatter
        self.filters = filters or []

    @_abstractmethod
    def handle(self, logger: "TurboPrint", record: _LogRecord) -> None:
        raise NotImplementedError()
