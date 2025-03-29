from abc import ABCMeta, abstractmethod
from datetime import time
from re import compile
from typing import (
    Protocol,
    runtime_checkable,
    Literal,
    Any,
    Optional,
    TYPE_CHECKING,
)
from src.my_types import LogRecord, LogLevel
import json

if TYPE_CHECKING:
    from src.turbo_print import TurboPrint

__all__ = [
    "BaseFilter",
    "LevelFilter",
    "RegexFilter",
    "TimeFilter",
    "ModuleFilter",
    "CompositeFilter",
    "TagFilter",
    "CategoryFilter",
    "MessageLengthFilter",
    "KeywordFilter",
]


@runtime_checkable
class FilterProtocol(Protocol):
    def filter(self, record: "LogRecord") -> bool: ...


class BaseFilter(metaclass=ABCMeta):
    """Базовый класс для фильтрации логов с поддержкой асинхронности."""

    def __init__(
        self,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            priority (int): Приоритет выполнения фильтра (чем меньше, тем раньше выполняется).
            logger (Optional[TurboPrint]): Логгер для записи действий фильтра.
            log_level (Optional[LogLevel]): Уровень логирования для фильтра.
        """
        self.priority = priority
        self.logger = logger
        self.log_level = log_level

    @abstractmethod
    async def filter(self, record: LogRecord) -> bool:
        """Асинхронная фильтрация записи лога.

        Args:
            record (LogRecord): Запись для фильтрации.

        Returns:
            bool: True, если запись должна быть обработана.
        """
        raise NotImplementedError

    async def log(self, message: str) -> None:
        """Асинхронное логирование действий фильтра.

        Args:
            message (str): Сообщение для логирования.
        """
        if self.logger and self.log_level:
            self.logger(message, self.log_level)

    def to_dict(self) -> dict[str, Any]:
        """Сериализует конфигурацию фильтра в словарь.

        Returns:
            Dict[str, Any]: Словарь с конфигурацией фильтра.
        """
        return {
            "priority": self.priority,
            "log_level": self.log_level.name if self.log_level else None,
        }

    def to_json(self) -> str:
        """Сериализует конфигурацию фильтра в JSON-строку.

        Returns:
            str: JSON-строка с конфигурацией фильтра.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    async def rollback(self, record: LogRecord) -> None:
        """Асинхронный откат изменений, внесенных фильтром.

        Args:
            record (LogRecord): Запись лога для отката.
        """
        await self.log(f"Откат изменений для записи: {record['message']}")


class LevelFilter(BaseFilter):
    """Фильтр по уровню логирования."""

    def __init__(
        self,
        level: LogLevel,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            level (LogLevel): Минимальный уровень для фильтрации.
            priority (int): Приоритет выполнения фильтра.
            logger (Optional[TurboPrint]): Логгер для записи действий фильтра.
            log_level (Optional[LogLevel]): Уровень логирования для фильтра.
        """
        super().__init__(priority, logger, log_level)
        self.level = level

    async def filter(self, record: LogRecord) -> bool:
        """Применить фильтр по уровню логирования.

        Args:
            record (LogRecord): Запись лога для проверки.

        Returns:
            bool: True, если уровень записи >= заданного уровня.
        """
        result = record["level"] >= self.level
        await self.log(f"Фильтрация по уровню: {record['level']}, результат: {result}")
        return result


class RegexFilter(BaseFilter):
    """Фильтрация по регулярному выражению."""

    def __init__(
        self,
        pattern: str,
        invert: bool = False,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            pattern (str): Регулярное выражение для фильтрации.
            invert (bool): Инвертировать результат фильтрации.
            priority (int): Приоритет выполнения фильтра.
            logger (Optional[TurboPrint]): Логгер для записи действий фильтра.
            log_level (Optional[LogLevel]): Уровень логирования для фильтра.
        """
        super().__init__(priority, logger, log_level)
        self.regex = compile(pattern)
        self.invert = invert

    async def filter(self, record: LogRecord) -> bool:
        """Проверяет соответствие сообщения регулярному выражению.

        Args:
            record (LogRecord): Запись лога для проверки.

        Returns:
            bool: True, если сообщение соответствует паттерну (или не соответствует при `invert=True`).
        """
        match = bool(self.regex.search(record["message"]))
        result = match if not self.invert else not match
        await self.log(
            f"Фильтрация по регулярному выражению: {record['message']}, результат: {result}"
        )
        return result


class TimeFilter(BaseFilter):
    """Фильтрация по времени суток."""

    def __init__(
        self,
        start_time: time,
        end_time: time,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            start_time (time): Время начала фильтрации.
            end_time (time): Время окончания фильтрации.
            priority (int): Приоритет выполнения фильтра.
            logger (Optional[TurboPrint]): Логгер для записи действий фильтра.
            log_level (Optional[LogLevel]): Уровень логирования для фильтра.
        """
        super().__init__(priority, logger, log_level)
        self.start = start_time
        self.end = end_time

    async def filter(self, record: LogRecord) -> bool:
        """Проверяет, попадает ли время записи в заданный диапазон.

        Args:
            record (LogRecord): Запись лога для проверки.

        Returns:
            bool: True, если время записи попадает в диапазон.
        """
        log_time = record["timestamp"].time()
        if self.start <= self.end:
            result = self.start <= log_time <= self.end
        else:
            result = log_time >= self.start or log_time <= self.end
        await self.log(f"Фильтрация по времени: {log_time}, результат: {result}")
        return result


class ModuleFilter(BaseFilter):
    """Фильтрация записей по имени модуля."""

    def __init__(
        self,
        module_name: str,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            module_name (str): Имя модуля для фильтрации.
            priority (int): Приоритет выполнения фильтра.
            logger (Optional[TurboPrint]): Логгер для записи действий фильтра.
            log_level (Optional[LogLevel]): Уровень логирования для фильтра.
        """
        super().__init__(priority, logger, log_level)
        self.module_name = module_name

    async def filter(self, record: LogRecord) -> bool:
        """Фильтрация по имени модуля.

        Args:
            record (LogRecord): Запись лога для проверки.

        Returns:
            bool: True, если имя модуля совпадает.
        """
        result = record["name"] == self.module_name
        await self.log(f"Фильтрация по модулю: {record['name']}, результат: {result}")
        return result


class CompositeFilter(BaseFilter):
    """Комбинирование фильтров через логические операции."""

    def __init__(
        self,
        filters: list[BaseFilter],
        mode: Literal["AND", "OR"] = "AND",
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            filters (List[BaseFilter]): Список фильтров.
            mode (Literal["AND", "OR"]): Режим комбинирования (AND или OR).
            priority (int): Приоритет выполнения фильтра.
            logger (Optional[TurboPrint]): Логгер для записи действий фильтра.
            log_level (Optional[LogLevel]): Уровень логирования для фильтра.
        """
        super().__init__(priority, logger, log_level)
        self.filters = filters
        self.mode = mode

    async def filter(self, record: LogRecord) -> bool:
        """Применяет комбинированный фильтр.

        Args:
            record (LogRecord): Запись лога для проверки.

        Returns:
            bool: Результат фильтрации.
        """
        filters = []
        for filter in self.filters:
            filters.append(await filter.filter(record))

        if self.mode == "AND":
            result = all(filters.copy())
        elif self.mode == "OR":
            result = any(filters.copy())
        else:
            result = False
        await self.log(
            f"Комбинированная фильтрация: {record['message']}, результат: {result}"
        )
        return result


class TagFilter(BaseFilter):
    """Фильтр по тегам."""

    def __init__(
        self,
        tags: list[str],
        match_all: bool = True,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            tags (List[str]): Список тегов для фильтрации.
            match_all (bool): Если True, все теги должны совпадать. Если False, достаточно одного совпадения.
            priority (int): Приоритет выполнения фильтра.
            logger (Optional[TurboPrint]): Логгер для записи действий фильтра.
            log_level (Optional[LogLevel]): Уровень логирования для фильтра.
        """
        super().__init__(priority, logger, log_level)
        self.tags = tags
        self.match_all = match_all

    async def filter(self, record: LogRecord) -> bool:
        """Фильтрация по тегам.

        Args:
            record (LogRecord): Запись лога для проверки.

        Returns:
            bool: Результат фильтрации.
        """
        if self.match_all:
            result = all(tag in record["tags"] for tag in self.tags)
        else:
            result = any(tag in record["tags"] for tag in self.tags)
        await self.log(f"Фильтрация по тегам: {record['tags']}, результат: {result}")
        return result


class CategoryFilter(BaseFilter):
    """Фильтр по категории."""

    def __init__(
        self,
        category: str,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            category (str): Категория для фильтрации.
            priority (int): Приоритет выполнения фильтра.
            logger (Optional[TurboPrint]): Логгер для записи действий фильтра.
            log_level (Optional[LogLevel]): Уровень логирования для фильтра.
        """
        super().__init__(priority, logger, log_level)
        self.category = category

    async def filter(self, record: LogRecord) -> bool:
        """Фильтрация по категории.

        Args:
            record (LogRecord): Запись лога для проверки.

        Returns:
            bool: Результат фильтрации.
        """
        result = record["category"] == self.category
        await self.log(
            f"Фильтрация по категории: {record['category']}, результат: {result}"
        )
        return result


class MessageLengthFilter(BaseFilter):
    """Фильтр по длине сообщения."""

    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            min_length (Optional[int]): Минимальная длина сообщения.
            max_length (Optional[int]): Максимальная длина сообщения.
            priority (int): Приоритет выполнения фильтра.
            logger (Optional[TurboPrint]): Логгер для записи действий фильтра.
            log_level (Optional[LogLevel]): Уровень логирования для фильтра.
        """
        super().__init__(priority, logger, log_level)
        self.min_length = min_length
        self.max_length = max_length

    async def filter(self, record: LogRecord) -> bool:
        """Фильтрация по длине сообщения.

        Args:
            record (LogRecord): Запись лога для проверки.

        Returns:
            bool: Результат фильтрации.
        """
        message_length = len(record["message"])
        result = True
        if self.min_length is not None:
            result = result and (message_length >= self.min_length)
        if self.max_length is not None:
            result = result and (message_length <= self.max_length)
        await self.log(
            f"Фильтрация по длине сообщения: {message_length}, результат: {result}"
        )
        return result


class KeywordFilter(BaseFilter):
    """Фильтр по наличию ключевых слов."""

    def __init__(
        self,
        keywords: list[str],
        case_sensitive: bool = False,
        priority: int = 0,
        logger: Optional["TurboPrint"] = None,
        log_level: Optional["LogLevel"] = None,
    ):
        """
        Args:
            keywords (List[str]): Список ключевых слов для фильтрации.
            case_sensitive (bool): Учитывать регистр при поиске.
            priority (int): Приоритет выполнения фильтра.
            logger (Optional[TurboPrint]): Логгер для записи действий фильтра.
            log_level (Optional[LogLevel]): Уровень логирования для фильтра.
        """
        super().__init__(priority, logger, log_level)
        self.keywords = keywords
        self.case_sensitive = case_sensitive

    async def filter(self, record: LogRecord) -> bool:
        """Фильтрация по наличию ключевых слов.

        Args:
            record (LogRecord): Запись лога для проверки.

        Returns:
            bool: Результат фильтрации.
        """
        message = (
            record["message"] if self.case_sensitive else record["message"].lower()
        )
        keywords = (
            self.keywords
            if self.case_sensitive
            else [kw.lower() for kw in self.keywords]
        )
        result = any(keyword in message for keyword in keywords)
        await self.log(
            f"Фильтрация по ключевым словам: {record['message']}, результат: {result}"
        )
        return result
