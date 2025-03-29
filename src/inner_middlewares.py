from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TextIO, Callable, Any, Optional

from src.my_types import LogRecord, LogLevel
from src.handlers import BaseHandler
import json

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint

__all__ = [
    "BaseInnerMiddleware",
    "ContextMiddleware",
    "FilterMiddleware",
    "MetadataMiddleware",
    "FormatMiddleware",
]


class BaseInnerMiddleware(ABC):
    """Базовый класс для внутренних middleware с поддержкой асинхронности."""

    def __init__(
        self,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            priority (int): Приоритет выполнения middleware (чем меньше, тем раньше выполняется).
            logger (Optional[TurboPrint]): Логгер для записи действий middleware.
            log_level (Optional[LogLevel]): Уровень логирования для middleware.
        """
        self.priority = priority
        self.logger = logger
        self.log_level = log_level

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

    async def log(self, message: str) -> None:
        """Асинхронное логирование действий middleware.

        Args:
            message (str): Сообщение для логирования.
        """
        if self.logger and self.log_level:
            self.logger(message, self.log_level)

    def to_dict(self) -> dict[str, Any]:
        """Сериализует конфигурацию middleware в словарь.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией middleware.
        """
        return {
            "priority": self.priority,
            "log_level": self.log_level.name if self.log_level else None,
        }

    def to_json(self) -> str:
        """Сериализует конфигурацию middleware в JSON-строку.

        Returns:
            str: JSON-строка с конфигурацией middleware.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    async def rollback(self, record: LogRecord) -> None:
        """Асинхронный откат изменений, внесенных middleware.

        Args:
            record (LogRecord): Запись лога для отката.
        """
        await self.log(f"Откат изменений для записи: {record['message']}")


class ContextMiddleware(BaseInnerMiddleware):
    """Middleware для добавления контекста в записи логов."""

    def __init__(
        self,
        context: dict[str, Any],
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            context (Dict[str, Any]): Контекст для добавления в запись лога.
            priority (int): Приоритет выполнения middleware.
            logger (Optional[TurboPrint]): Логгер для записи действий middleware.
            log_level (Optional[LogLevel]): Уровень логирования для middleware.
        """
        super().__init__(priority, logger, log_level)
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
        await self.log(f"Добавление контекста: {self.context}")
        record["extra"] = {**record["extra"], **self.context}
        return True


class FilterMiddleware(BaseInnerMiddleware):
    """Middleware для фильтрации записей логов."""

    def __init__(
        self,
        filter_func: Callable,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            filter_func (Callable): Функция для фильтрации записей.
            priority (int): Приоритет выполнения middleware.
            logger (Optional[TurboPrint]): Логгер для записи действий middleware.
            log_level (Optional[LogLevel]): Уровень логирования для middleware.
        """
        super().__init__(priority, logger, log_level)
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
        result = self.filter_func(record)
        await self.log(f"Фильтрация записи: {record['message']}, результат: {result}")
        return result


class MetadataMiddleware(BaseInnerMiddleware):
    """Middleware для добавления метаданных в записи логов."""

    def __init__(
        self,
        metadata: dict[str, Any],
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            metadata (Dict[str, Any]): Метаданные для добавления в запись лога.
            priority (int): Приоритет выполнения middleware.
            logger (Optional[TurboPrint]): Логгер для записи действий middleware.
            log_level (Optional[LogLevel]): Уровень логирования для middleware.
        """
        super().__init__(priority, logger, log_level)
        self.metadata = metadata

    async def __call__(
        self,
        handler: BaseHandler,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        """Асинхронное добавление метаданных в запись лога.

        Args:
            handler (BaseHandler): Обработчик логов.
            logger (TurboPrint): Логгер.
            record (LogRecord): Запись лога.
            stdout (TextIO): Стандартный вывод.
            stderr (TextIO): Стандартный вывод ошибок.

        Returns:
            bool: Всегда возвращает True.
        """
        await self.log(f"Добавление метаданных: {self.metadata}")
        record["extra"] = {**record["extra"], **self.metadata}
        return True


class FormatMiddleware(BaseInnerMiddleware):
    """Middleware для изменения формата сообщения лога."""

    def __init__(
        self,
        format_func: Callable,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            format_func (Callable): Функция для изменения формата сообщения.
            priority (int): Приоритет выполнения middleware.
            logger (Optional[TurboPrint]): Логгер для записи действий middleware.
            log_level (Optional[LogLevel]): Уровень логирования для middleware.
        """
        super().__init__(priority, logger, log_level)
        self.format_func = format_func

    async def __call__(
        self,
        handler: BaseHandler,
        logger: "TurboPrint",
        record: LogRecord,
        stdout: TextIO,
        stderr: TextIO,
    ) -> bool:
        """Асинхронное изменение формата сообщения лога.

        Args:
            handler (BaseHandler): Обработчик логов.
            logger (TurboPrint): Логгер.
            record (LogRecord): Запись лога.
            stdout (TextIO): Стандартный вывод.
            stderr (TextIO): Стандартный вывод ошибок.

        Returns:
            bool: Всегда возвращает True.
        """
        await self.log(f"Изменение формата сообщения: {record['message']}")
        record["message"] = self.format_func(record["message"])
        return True
