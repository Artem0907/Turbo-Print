from abc import ABC, abstractmethod
from io import StringIO
from colorama import Style
from yaml import dump as yaml_dump
from ujson import dumps as json_dump
from csv import DictWriter
from typing import Optional, Any, Dict, List, TYPE_CHECKING
from string import Formatter
from datetime import datetime
import json

from src.my_types import LogRecord, LogLevel
from src.localization import Localization

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint

__all__ = [
    "BaseFormatter",
    "DefaultFormatter",
    "JSONFormatter",
    "XMLFormatter",
    "YAMLFormatter",
    "CSVFormatter",
    "HTMLFormatter",
    "MarkdownFormatter",
    "CustomFormatter",
    "PlainTextFormatter",
    "TemplateFormatter",
]


class BaseFormatter(ABC):
    """Базовый класс для форматирования записей логов с поддержкой асинхронности."""

    def __init__(
        self,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            priority (int): Приоритет выполнения форматера (чем меньше, тем раньше выполняется).
            logger (Optional[TurboPrint]): Логгер для записи действий форматера.
            log_level (Optional[LogLevel]): Уровень логирования для форматера.
        """
        self.priority = priority
        self.logger = logger
        self.log_level = log_level

    @abstractmethod
    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка.
        """
        raise NotImplementedError

    async def format_colored(self, record: LogRecord) -> str:
        """Асинхронное цветное форматирование записи.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка с цветами.
        """
        return await self.format(record)

    async def log(self, message: str) -> None:
        """Асинхронное логирование действий форматера.

        Args:
            message (str): Сообщение для логирования.
        """
        if self.logger and self.log_level:
            self.logger(message, self.log_level)

    def to_dict(self) -> Dict[str, Any]:
        """Сериализует конфигурацию форматера в словарь.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией форматера.
        """
        return {
            "priority": self.priority,
            "log_level": self.log_level.name if self.log_level else None,
        }

    def to_json(self) -> str:
        """Сериализует конфигурацию форматера в JSON-строку.

        Returns:
            str: JSON-строка с конфигурацией форматера.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    async def rollback(self, record: LogRecord) -> None:
        """Асинхронный откат изменений, внесенных форматером.

        Args:
            record (LogRecord): Запись лога для отката.
        """
        await self.log(f"Откат изменений для записи: {record['message']}")


class DefaultFormatter(BaseFormatter):
    """Форматтер по умолчанию с поддержкой локализации и асинхронного форматирования."""

    def __init__(
        self,
        fmt: str = "[{time}] {prefix} | {level_name}[{level_value}]: {message}",
        localization: Optional[Localization] = None,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            fmt (str): Шаблон форматирования.
            localization (Optional[Localization]): Локализация.
            priority (int): Приоритет выполнения форматера.
            logger (Optional[TurboPrint]): Логгер для записи действий форматера.
            log_level (Optional[LogLevel]): Уровень логирования для форматера.
        """
        super().__init__(priority, logger, log_level)
        self._fmt = fmt
        self.localization = localization or Localization()

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование сообщения.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка.
        """
        data = {
            "time": self.localization.format_datetime(record["timestamp"]),
            "name": record["name"],
            "prefix": record["prefix"] or record["name"],
            "level_name": await self.localization.translate(
                record["level"].name.lower()
            ),
            "level_value": record["level"].value,
            **record["extra"],
        }
        formatted_message = self._fmt.format(
            **data, message=record["message"].format(**data)
        )
        await self.log(f"Форматирование записи: {record['message']}")
        return formatted_message

    async def format_colored(self, record: LogRecord) -> str:
        """Асинхронное цветное форматирование сообщения.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка с цветами.
        """
        base = await self.format(record)
        return f"{record['level'].color}{base}{Style.RESET_ALL}"


class JSONFormatter(BaseFormatter):
    """Форматтер для формирования JSON-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в JSON-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: JSON-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        formatted_message = json_dump(log_data, ensure_ascii=False)
        await self.log(f"Форматирование записи в JSON: {record['message']}")
        return formatted_message


class XMLFormatter(BaseFormatter):
    """Форматтер для формирования XML-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в XML-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: XML-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        formatted_message = (
            f"<log>{''.join(f'<{k}>{v}</{k}>' for k, v in log_data.items())}</log>"
        )
        await self.log(f"Форматирование записи в XML: {record['message']}")
        return formatted_message


class YAMLFormatter(BaseFormatter):
    """Форматтер для формирования YAML-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в YAML-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: YAML-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        formatted_message = yaml_dump(log_data, default_flow_style=False)
        await self.log(f"Форматирование записи в YAML: {record['message']}")
        return formatted_message


class CSVFormatter(BaseFormatter):
    """Форматтер для формирования CSV-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в CSV-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: CSV-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        output = StringIO()
        writer = DictWriter(output, fieldnames=log_data.keys())
        writer.writeheader()
        writer.writerow(log_data)
        formatted_message = output.getvalue()
        await self.log(f"Форматирование записи в CSV: {record['message']}")
        return formatted_message


class HTMLFormatter(BaseFormatter):
    """Форматтер для формирования HTML-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в HTML-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: HTML-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        formatted_message = (
            "<div class='log-entry'>"
            + "".join(f"<p><b>{k}:</b> {v}</p>" for k, v in log_data.items())
            + "</div>"
        )
        await self.log(f"Форматирование записи в HTML: {record['message']}")
        return formatted_message


class MarkdownFormatter(BaseFormatter):
    """Форматтер для формирования Markdown-строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в Markdown-строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Markdown-строка.
        """
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        formatted_message = "\n".join(f"**{k}:** {v}" for k, v in log_data.items())
        await self.log(f"Форматирование записи в Markdown: {record['message']}")
        return formatted_message


class CustomFormatter(BaseFormatter):
    """Форматтер для создания пользовательских форматов логов."""

    def __init__(
        self,
        fmt: str,
        macros: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            fmt (str): Шаблон форматирования.
            macros (Optional[Dict[str, Any]]): Пользовательские макросы.
            priority (int): Приоритет выполнения форматера.
            logger (Optional[TurboPrint]): Логгер для записи действий форматера.
            log_level (Optional[LogLevel]): Уровень логирования для форматера.
        """
        super().__init__(priority, logger, log_level)
        self._fmt = fmt
        self._macros = macros or {}

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи с использованием пользовательского шаблона и макросов.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка.
        """
        formatter = Formatter()
        data = {
            "time": record["timestamp"].strftime("%H:%M:%S"),
            "name": record["name"],
            "prefix": record["prefix"] or record["name"],
            "level_name": record["level"].name,
            "level_value": record["level"].value,
            **record["extra"],
            **self._macros,  # Добавляем пользовательские макросы
        }
        formatted_message = formatter.format(self._fmt, **data)
        await self.log(
            f"Форматирование записи с пользовательским шаблоном: {record['message']}"
        )
        return formatted_message


class PlainTextFormatter(BaseFormatter):
    """Форматтер для формирования Plain Text строки."""

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи в Plain Text строку.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Plain Text строка.
        """
        formatted_message = (
            f"{record['timestamp']} {record['level'].name}: {record['message']}"
        )
        await self.log(f"Форматирование записи в Plain Text: {record['message']}")
        return formatted_message


class TemplateFormatter(BaseFormatter):
    """Форматтер для форматирования с использованием шаблонов."""

    def __init__(
        self,
        template: str,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            template (str): Шаблон для форматирования.
            priority (int): Приоритет выполнения форматера.
            logger (Optional[TurboPrint]): Логгер для записи действий форматера.
            log_level (Optional[LogLevel]): Уровень логирования для форматера.
        """
        super().__init__(priority, logger, log_level)
        self.template = template

    async def format(self, record: LogRecord) -> str:
        """Асинхронное форматирование записи с использованием шаблона.

        Args:
            record (LogRecord): Запись лога.

        Returns:
            str: Отформатированная строка.
        """
        formatted_message = self.template.format(
            timestamp=record["timestamp"],
            level=record["level"].name,
            message=record["message"],
            **record["extra"],
        )
        await self.log(
            f"Форматирование записи с использованием шаблона: {record['message']}"
        )
        return formatted_message
