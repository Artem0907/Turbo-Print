from abc import ABC, abstractmethod
from io import StringIO
from colorama import Style
from yaml import dump as yaml_dump
from ujson import dumps as json_dump
from csv import DictWriter

from src.my_types import LogRecord

__all__ = ["BaseFormatter", "DefaultFormatter", "JSONFormatter"]


class BaseFormatter(ABC):
    """Базовый класс для форматирования записей."""

    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """Форматирование записи в строку."""
        raise NotImplementedError

    def format_colored(self, record: LogRecord) -> str:
        """Цветное форматирование записи."""
        return self.format(record)


class DefaultFormatter(BaseFormatter):
    """Форматтер по умолчанию с поддержкой цветов.

    Пример:
    >>> formatter = DefaultFormatter()
    >>> record = LogRecord(message="Test", level=LogLevel.INFO, ...)
    >>> formatted = formatter.format(record)
    >>> "[12:34:56] root | INFO[20]: Test" in formatted
    True
    """

    def __init__(
        self, fmt: str = "[{time}] {prefix} | {level_name}[{level_value}]: {message}"
    ) -> None:
        """
        Args:
            fmt (str): Шаблон форматирования
        """
        self._fmt = fmt

    def format(self, record: LogRecord) -> str:
        """Основное форматирование сообщения."""
        data = {
            "time": record["timestamp"].strftime("%H:%M:%S"),
            "prefix": record["prefix"] or record["name"],
            "level_name": record["level"].name,
            "level_value": record["level"].value,
            "message": record["message"],
            **record["extra"],
        }
        return self._fmt.format(**data)

    def format_colored(self, record: LogRecord) -> str:
        """Добавление цветовой подсветки к сообщению."""
        base = self.format(record)
        return f"{record['level'].color}{base}{Style.RESET_ALL}"


class JSONFormatter(BaseFormatter):
    """Форматтер для формирования JSON-строки."""

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в JSON-строку."""
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return json_dump(log_data, ensure_ascii=False)


class XMLFormatter(BaseFormatter):
    """Форматтер для формирования XML-строки."""

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в XML-строку."""
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return f"<log>{''.join(f'<{k}>{v}</{k}>' for k, v in log_data.items())}</log>"


class YAMLFormatter(BaseFormatter):
    """Форматтер для формирования YAML-строки."""

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в YAML-строку."""
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return yaml_dump(log_data, default_flow_style=False)


class CSVFormatter(BaseFormatter):
    """Форматтер для формирования CSV-строки."""

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в CSV-строку."""
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
        return output.getvalue()


class HTMLFormatter(BaseFormatter):
    """Форматтер для формирования HTML-строки."""

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в HTML-строку."""
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return (
            "<div class='log-entry'>"
            + "".join(f"<p><b>{k}:</b> {v}</p>" for k, v in log_data.items())
            + "</div>"
        )

class MarkdownFormatter(BaseFormatter):
    """Форматтер для формирования Markdown-строки."""

    def format(self, record: LogRecord) -> str:
        """Форматирование записи в Markdown-строку."""
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "timestamp": record["timestamp"].isoformat(),
            "parent": repr(record["parent"]),
        }
        return "\n".join(f"**{k}:** {v}" for k, v in log_data.items())