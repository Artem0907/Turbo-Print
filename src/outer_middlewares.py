from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TextIO, Callable
from src.my_types import LogRecord
from src.handlers import BaseHandler

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint


class BaseOuterMiddleware(ABC):
    """Базовый класс для внешних middleware с поддержкой асинхронности."""

    @abstractmethod
    async def __call__(
        self,
        handler: BaseHandler,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        """Асинхронный вызов middleware.

        Args:
            handler (BaseHandler): Обработчик логов.
            logger (TurboPrint): Логгер.
            record (LogRecord): Запись лога.
            stdout (TextIO): Стандартный вывод.
            stderr (TextIO): Стандартный вывод ошибок.

        Returns:
            bool: Результат выполнения middleware.
        """
        raise NotImplementedError


class ContextMiddleware(BaseOuterMiddleware):
    """Middleware для добавления контекста в записи логов."""

    def __init__(self, **context) -> None:
        """
        Args:
            **context: Контекст для добавления в запись лога.
        """
        self.context = context

    async def __call__(
        self,
        handler: BaseHandler,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        """Асинхронное добавление контекста в запись лога.

        Args:
            handler (BaseHandler): Обработчик логов.
            logger (TurboPrint): Логгер.
            record (LogRecord): Запись лога.
            stdout (TextIO): Стандартный вывод.
            stderr (TextIO): Стандартный вывод ошибок.

        Returns:
            bool: Всегда возвращает True.
        """
        record["extra"] = {**record["extra"], **self.context}
        return True


class AsyncFilterMiddleware(BaseOuterMiddleware):
    """Асинхронное middleware для фильтрации записей логов."""

    def __init__(self, filter_func: Callable) -> None:
        """
        Args:
            filter_func (callable): Асинхронная функция для фильтрации записей.
        """
        self.filter_func = filter_func

    async def __call__(
        self,
        handler: BaseHandler,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        """Асинхронная фильтрация записи лога.

        Args:
            handler (BaseHandler): Обработчик логов.
            logger (TurboPrint): Логгер.
            record (LogRecord): Запись лога.
            stdout (TextIO): Стандартный вывод.
            stderr (TextIO): Стандартный вывод ошибок.

        Returns:
            bool: Результат фильтрации.
        """
        return await self.filter_func(record)