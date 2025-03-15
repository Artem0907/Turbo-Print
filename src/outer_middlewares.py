from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TextIO

from src.my_types import LogRecord
from src.handlers import BaseHandler

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint


class BaseOuterMiddleware(ABC):
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
