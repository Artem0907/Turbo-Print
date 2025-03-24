from typing import Optional, Dict, Any, TYPE_CHECKING
from traceback import format_exc
from datetime import datetime
from src.my_types import LogLevel
import json

if TYPE_CHECKING:
    from .turbo_print import TurboPrint

__all__ = [
    "CustomException",
    "CompressionError",
    "DecompressionError",
    "LoggingError",
    "SerializationError",
]


class CustomException(Exception):
    """Кастомное исключение с поддержкой логирования и асинхронного вызова."""

    def __init__(
        self,
        message: str,
        logger: Optional["TurboPrint"] = None,
        level: LogLevel = LogLevel.ERROR,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message (str): Сообщение об ошибке.
            logger (Optional[TurboPrint]): Логгер для записи исключения.
            level (LogLevel): Уровень логирования (по умолчанию ERROR).
            context (Optional[Dict[str, Any]]): Дополнительный контекст для логирования.
        """
        super().__init__(message)
        self.message = message
        self.logger = logger
        self.level = level
        self.context = context or {}
        self.stack_trace = format_exc()
        self.timestamp = datetime.now()

        # Логирование исключения, если передан логгер
        if self.logger:
            self.log()

    def log(self) -> None:
        """Синхронное логирование исключения с дополнительной информацией."""
        if self.logger:
            self.logger(
                f"Исключение: {self.message}",
                self.level,
                stack_trace=self.stack_trace,
                timestamp=self.timestamp.isoformat(),
                **self.context,
            )

    async def log_async(self) -> None:
        """Асинхронное логирование исключения с дополнительной информацией."""
        if self.logger:
            self.logger(
                f"Исключение: {self.message}",
                self.level,
                stack_trace=self.stack_trace,
                timestamp=self.timestamp.isoformat(),
                **self.context,
            )

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает исключение в виде словаря.

        Returns:
            Dict[str, Any]: Словарь с информацией об исключении.
        """
        return {
            "message": self.message,
            "level": self.level.name,
            "stack_trace": self.stack_trace,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }

    def to_json(self) -> str:
        """Сериализует исключение в JSON-строку.

        Returns:
            str: JSON-строка с информацией об исключении.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __str__(self) -> str:
        """Возвращает строковое представление исключения.

        Returns:
            str: Строковое представление исключения.
        """
        return f"{self.message}\nStack Trace:\n{self.stack_trace}"


class CompressionError(CustomException):
    """Исключение, связанное с ошибками сжатия."""

    def __init__(
        self,
        message: str,
        logger: Optional["TurboPrint"] = None,
        level: LogLevel = LogLevel.ERROR,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, logger, level, context)


class DecompressionError(CustomException):
    """Исключение, связанное с ошибками распаковки."""

    def __init__(
        self,
        message: str,
        logger: Optional["TurboPrint"] = None,
        level: LogLevel = LogLevel.ERROR,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, logger, level, context)


class LoggingError(CustomException):
    """Исключение, связанное с ошибками логирования."""

    def __init__(
        self,
        message: str,
        logger: Optional["TurboPrint"] = None,
        level: LogLevel = LogLevel.ERROR,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, logger, level, context)


class SerializationError(CustomException):
    """Исключение, связанное с ошибками сериализации."""

    def __init__(
        self,
        message: str,
        logger: Optional["TurboPrint"] = None,
        level: LogLevel = LogLevel.ERROR,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, logger, level, context)


class RecoveryMixin:
    """Миксин для восстановления состояния после исключения."""

    def recover(self) -> bool:
        """Попытка восстановления состояния после исключения.

        Returns:
            bool: True, если восстановление успешно, иначе False.
        """
        # Пример реализации восстановления (может быть переопределен в дочерних классах)
        return False
