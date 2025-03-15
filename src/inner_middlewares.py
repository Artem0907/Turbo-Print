from abc import ABC, abstractmethod
from asyncio import iscoroutinefunction
from typing import TYPE_CHECKING, TextIO

from src.my_types import LogRecord
from src.handlers import BaseHandler

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint


class BaseInnerMiddleware(ABC):
    @abstractmethod
    async def __call__(
        self,
        handler: BaseHandler,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        raise NotImplementedError


class ContextMiddleware(BaseInnerMiddleware):
    """Middleware для добавления контекста в записи логов."""

    def __init__(self, **context) -> None:
        self.context = context

    async def __call__(
        self,
        handler: BaseHandler,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        record["extra"] = {**record["extra"], **self.context}
        return True
