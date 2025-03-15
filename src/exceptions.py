from typing import Optional, Dict, Any
from traceback import format_exc
from src.turbo_print import TurboPrint
from src.my_types import LogLevel


class CustomException(Exception):
    """Кастомное исключение с поддержкой логирования."""

    def __init__(
        self,
        message: str,
        logger: Optional[TurboPrint] = None,
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

        # Логирование исключения, если передан логгер
        if self.logger:
            self.log()

    def log(self) -> None:
        """Логирует исключение с дополнительной информацией."""
        if self.logger:
            self.logger(
                f"Исключение: {self.message}",
                self.level,
                stack_trace=self.stack_trace,
                **self.context,
            )
