from asyncio import (
    AbstractEventLoop,
    get_running_loop,
    get_event_loop,
    iscoroutinefunction,
)
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from dotenv import load_dotenv
from functools import wraps
from logging import Logger
from pathlib import Path
from time import time
from traceback import format_exc
from typing import ClassVar, Optional, Callable, Any, TextIO, TypeVar, cast
import sys

# from config_loader import ConfigLoader
from src import formatters, handlers, filters
from src.filters import BaseFilter
from src.formatters import BaseFormatter, DefaultFormatter
from src.handlers import (
    BaseHandler,
    StreamHandler,
    BufferedFileHandler,
    FileHandler,
    TimedRotatingFileHandler,
)
from src.inner_middlewares import BaseInnerMiddleware
from src.localization import Localization
from src.metrics import Metrics
from src.migration import LoggingAdapter
from src.my_types import LogLevel, TurboPrintOutput, LogRecord, TurboPrintConfig
from src.outer_middlewares import BaseOuterMiddleware
from src.realtime import RealTimeLogger


try:
    _DEFAULT_ASYNC_LOOP = get_running_loop()
except RuntimeError:
    _DEFAULT_ASYNC_LOOP = get_event_loop()

ROOT_LOGGER_NAME = "root"


class TurboPrint:
    _context: ContextVar[dict[str, Any]] = ContextVar("context", default={})
    _registry: ClassVar[dict[str, "TurboPrint"]] = {}
    _root_logger: ClassVar["TurboPrint"]

    @classmethod
    def _init_root_logger(cls) -> None:
        """Инициализация корневого логгера."""
        if hasattr(cls, "_root_logger"):
            return

        cls._root_logger = None  # type:  ignore
        root = cls(
            ROOT_LOGGER_NAME,
            prefix="ROOT",
            level=LogLevel.INFO,
            propagate=False,
            handlers=[StreamHandler()],
        )
        cls._root_logger = root
        cls._registry[ROOT_LOGGER_NAME] = root

    @classmethod
    def get_logger(cls, name: Optional[str] = None, **kwargs: Any) -> "TurboPrint":
        """Фабричный метод для получения или создания логгера.

        Args:
            name (Optional[str]): Имя логгера.
            **kwargs: Дополнительные параметры.

        Returns:
            TurboPrint: Логгер.
        """
        if not hasattr(cls, "_root_logger"):
            cls._init_root_logger()

        if name is None:
            return cls._root_logger

        if name in cls._registry:
            return cls._registry[name]

        if "." in name:
            parent_name, _, child_name = name.rpartition(".")
            parent = cls.get_logger(parent_name)
            return cls(name=name, parent=parent, **kwargs)

        return cls(name=name, parent=cls._root_logger, **kwargs)

    @staticmethod
    async def from_logging(logger: Logger) -> "TurboPrint":
        """Создает логгер TurboPrint на основе логгера logging.

        Args:
            logger (Logger): Логгер из модуля logging.

        Returns:
            TurboPrint: Логгер TurboPrint.
        """
        adapter = LoggingAdapter()
        await adapter.migrate_logger(logger)
        return adapter.logger

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        enabled: bool = True,
        prefix: Optional[str] = None,
        level: LogLevel = LogLevel.NOTSET,
        parent: Optional["TurboPrint"] = None,
        propagate: bool = True,
        handlers: Optional[list[BaseHandler]] = None,
        filters: Optional[list[BaseFilter]] = None,
        inner_middlewares: Optional[list[BaseInnerMiddleware]] = None,
        outer_middlewares: Optional[list[BaseOuterMiddleware]] = None,
        formatter: BaseFormatter = DefaultFormatter(),
        async_loop: AbstractEventLoop = _DEFAULT_ASYNC_LOOP,
        stderr: TextIO = sys.stderr,
        stdout: TextIO = sys.stdout,
        inherit_filters: bool = True,
        inherit_handlers: bool = True,
        inherit_formatter: bool = True,
        metrics: Optional[Metrics] = None,
        localization: Optional[Localization] = None,
        realtime_logger: Optional[RealTimeLogger] = None,
    ) -> None:
        """Инициализация логгера.

        Args:
            name (Optional[str]): Имя логгера.
            enabled (bool): Включен ли логгер.
            prefix (Optional[str]): Префикс для логов.
            level (LogLevel): Уровень логирования.
            parent (Optional["TurboPrint"]): Родительский логгер.
            propagate (bool): Распространять ли логи на родительский логгер.
            handlers (Optional[list[BaseHandler]]): Обработчики логов.
            filters (Optional[list[BaseFilter]]): Фильтры логов.
            inner_middlewares (Optional[list[BaseInnerMiddleware]]): Внутренние middleware.
            outer_middlewares (Optional[list[BaseOuterMiddleware]]): Внешние middleware.
            formatter (BaseFormatter): Форматтер логов.
            async_loop (AbstractEventLoop): Цикл событий для асинхронных операций.
            stderr (TextIO): Стандартный вывод ошибок.
            stdout (TextIO): Стандартный вывод.
            inherit_filters (bool): Наследовать ли фильтры от родительского логгера.
            inherit_handlers (bool): Наследовать ли обработчики от родительского логгера.
            inherit_formatter (bool): Наследовать ли форматтер от родительского логгера.
            metrics (Optional[Metrics]): Метрики.
            localization (Optional[Localization]): Локализация.
            realtime_logger (Optional[RealTimeLogger]): Логгер для логирования в реальном времени.
        """
        if not hasattr(TurboPrint, "_root_logger"):
            TurboPrint._init_root_logger()

        self.stderr = stderr
        self.stdout = stdout
        self.name = name or str(id(self))
        self.enabled = enabled
        self.async_loop = async_loop
        self.prefix = prefix
        self.level = level
        self.parent = parent if parent else self._root_logger
        self.propagate = propagate
        self.handlers = handlers or []
        self.inner_middlewares = inner_middlewares or []
        self.outer_middlewares = outer_middlewares or []
        self._logger_filters = filters or []
        self.formatter = formatter
        self._children: list[TurboPrint] = []
        self.inherit_filters = inherit_filters
        self.inherit_handlers = inherit_handlers
        self.inherit_formatter = inherit_formatter
        self.metrics = metrics
        self._tags: list[str] = []
        self._category: Optional[str] = None
        self.localization = localization or Localization()
        self.realtime_logger = realtime_logger

        if self.name in TurboPrint._registry:
            stderr.write(f"ValueError: Логгер '{self.name}' уже существует" + "\n")
            stderr.flush()

        if self.parent:
            self.parent._add_child(self)

        TurboPrint._registry[self.name] = self

    def __call__(self, message: str, level: LogLevel = LogLevel.NOTSET, **kwargs: Any):
        """Асинхронный метод логирования.

        Args:
            message (str): Сообщение для логирования.
            level (LogLevel): Уровень логирования.
            **kwargs: Дополнительные данные.

        Returns:
            TurboPrintOutput: Результат логирования.
        """
        if not self.enabled or level < self.level:
            return False

        localized_message = self.async_loop.run_until_complete(
            self.localization.translate(message)
        )

        record = LogRecord(
            message=localized_message,
            name=self.name,
            level=level,
            prefix=self.prefix,
            timestamp=datetime.now(),
            parent=self.parent,
            extra={**self._context.get(), **kwargs},
            tags=self._tags.copy(),
            category=self._category,
        )

        # Применяем фильтры на уровне логгера
        if any(not f.filter(record) for f in self.get_filters()):
            return False

        # Запуск асинхронной обработки записи
        self.async_loop.run_until_complete(self._process_record_async(record))

        if self.parent and self.propagate:
            self.async_loop.run_until_complete(self.parent._propagate_async(record))

        return TurboPrintOutput(
            colored_console=self.async_loop.run_until_complete(
                self.get_formatter().format_colored(record)
            ),
            standard_file=self.async_loop.run_until_complete(
                self.get_formatter().format(record)
            ),
        )

    async def _process_record_async(self, record: LogRecord) -> None:
        """Асинхронная обработка записи лога.

        Args:
            record (LogRecord): Запись лога.
        """
        if self.realtime_logger:
            await self.realtime_logger.log(
                {
                    "message": record["message"],
                    "level": record["level"].name,
                    "timestamp": record["timestamp"].isoformat(),
                    **record["extra"],
                }
            )

        await self._start_handlers(record)

    async def _propagate_async(self, record: LogRecord) -> None:
        """Асинхронное распространение записи по иерархии.

        Args:
            record (LogRecord): Запись лога.
        """
        new_record = record.copy()
        new_record["name"] = self.name
        new_record["prefix"] = self.prefix
        new_record["parent"] = self.parent

        if self.level <= new_record["level"]:
            await self._process_record_async(new_record)

        if self.parent and self.propagate:
            await self.parent._propagate_async(new_record)

    def _add_child(self, child: "TurboPrint") -> None:
        """Добавление дочернего логгера.

        Args:
            child (TurboPrint): Дочерний логгер.
        """
        self._children.append(child)

    async def _start_handlers(self, record: LogRecord) -> None:
        """Асинхронный запуск обработчиков с обработкой ошибок.

        Args:
            record (LogRecord): Запись лога.
        """
        start_time = datetime.now()
        try:
            for handler in self.get_handlers():
                try:
                    for inner_middleware in self.inner_middlewares:
                        await inner_middleware(
                            handler, self, record, self.stdout, self.stderr
                        )
                    await handler.handle(self, record, self.stdout, self.stderr)
                    for outer_middleware in self.outer_middlewares:
                        await outer_middleware(
                            handler, self, record, self.stdout, self.stderr
                        )
                except Exception as e:
                    self.stderr.write(f"Ошибка обработчика {handler}: {e}")
                    self.stderr.flush()
                    if self.metrics:
                        await self.metrics.error_occurred()
        finally:
            if self.metrics:
                processing_time = (datetime.now() - start_time).total_seconds()
                await self.metrics.log_processed(record["level"].name, processing_time)

    def set_context(self, **kwargs: Any) -> None:
        """Устанавливает контекст для логгера.

        Args:
            **kwargs: Контекст.
        """
        self._context.set(kwargs)

    def add_custom_level(self, name: str, value: int, color: str) -> LogLevel:
        """Добавляет кастомный уровень логирования.

        Args:
            name (str): Имя уровня.
            value (int): Значение уровня.
            color (str): Цвет для отображения в консоли.

        Returns:
            LogLevel: Новый уровень логирования.
        """
        return LogLevel.add_custom_level(name, value, color)

    def get_level(self) -> LogLevel:
        """Возвращает текущий уровень логирования.

        Returns:
            LogLevel: Текущий уровень логирования.
        """
        return self.level

    def set_level(self, level: LogLevel) -> None:
        """Устанавливает уровень логирования.

        Args:
            level (LogLevel): Уровень логирования.
        """
        self.level = level

    def add_handler(self, handler: BaseHandler) -> None:
        """Добавляет обработчик.

        Args:
            handler (BaseHandler): Обработчик.
        """
        self.handlers.append(handler)

    def get_handlers(self) -> list[BaseHandler]:
        """Возвращает список обработчиков.

        Returns:
            list[BaseHandler]: Список обработчиков.
        """
        return self.handlers

    def remove_handler(self, handler: BaseHandler) -> None:
        """Удаляет обработчик.

        Args:
            handler (BaseHandler): Обработчик.
        """
        self.handlers.remove(handler)

    def set_formatter(self, formatter: BaseFormatter) -> None:
        """Устанавливает форматтер.

        Args:
            formatter (BaseFormatter): Форматтер.
        """
        self.formatter = formatter

    def get_formatter(self) -> BaseFormatter:
        """Возвращает форматтер.

        Returns:
            BaseFormatter: Форматтер.
        """
        return self.formatter

    def add_filter(self, filter: BaseFilter) -> None:
        """Добавляет фильтр.

        Args:
            filter (BaseFilter): Фильтр.
        """
        self._logger_filters.append(filter)

    def add_tag(self, tag: str) -> None:
        """Добавляет тег к логгеру.

        Args:
            tag (str): Тег.
        """
        self._tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Удаляет тег из логгера.

        Args:
            tag (str): Тег.
        """
        self._tags.remove(tag)

    def set_category(self, category: str) -> None:
        """Устанавливает категорию для логгера.

        Args:
            category (str): Категория.
        """
        self._category = category

    def get_filters(self) -> list[BaseFilter]:
        """Возвращает список фильтров.

        Returns:
            list[BaseFilter]: Список фильтров.
        """
        return (
            self._logger_filters + self.parent.get_filters()
            if self.parent
            else self._logger_filters
        )

    def remove_filter(self, filter: BaseFilter) -> None:
        """Удаляет фильтр.

        Args:
            filter (BaseFilter): Фильтр.
        """
        self._logger_filters.remove(filter)

    def update_config(self, config: dict[str, Any]) -> None:
        """Обновляет конфигурацию логгера на лету.

        Args:
            config (dict[str, Any]): Конфигурация.
        """
        if "level" in config:
            self.set_level(LogLevel[config["level"]])

        if "formatter" in config:
            formatter_config = config["formatter"]
            formatter_type = formatter_config.get("type", "default")
            if formatter_type == "json":
                self.set_formatter(formatters.JSONFormatter())
            elif formatter_type == "xml":
                self.set_formatter(formatters.XMLFormatter())
            elif formatter_type == "yaml":
                self.set_formatter(formatters.YAMLFormatter())
            elif formatter_type == "csv":
                self.set_formatter(formatters.CSVFormatter())
            elif formatter_type == "html":
                self.set_formatter(formatters.HTMLFormatter())
            elif formatter_type == "markdown":
                self.set_formatter(formatters.MarkdownFormatter())
            else:
                self.set_formatter(formatters.DefaultFormatter())

        if "handlers" in config:
            for handler_config in config["handlers"]:
                handler_type = handler_config.get("type")
                if handler_type == "stream":
                    self.add_handler(handlers.StreamHandler())
                elif handler_type == "file":
                    self.add_handler(
                        handlers.FileHandler(
                            Path(handler_config.get("file_directory", "logs"))
                        )
                    )
                elif handler_type == "timed_rotating_file":
                    self.add_handler(
                        handlers.TimedRotatingFileHandler(
                            Path(handler_config.get("file_directory", "logs")),
                            when=handler_config.get("when", "D"),
                            interval=handler_config.get("interval", 1),
                            backup_count=handler_config.get("backup_count", 5),
                            compress=handler_config.get("compress", False),
                            compress_format=handler_config.get(
                                "compress_format", "gzip"
                            ),
                        )
                    )
                elif handler_type == "size_rotating_file":
                    self.add_handler(
                        handlers.SizeRotatingFileHandler(
                            Path(handler_config.get("file_directory", "logs")),
                            max_size=handler_config.get(
                                "max_size", 10 * 1024 * 1024
                            ),  # 10 MB
                            backup_count=handler_config.get("backup_count", 5),
                        )
                    )

        if "filters" in config:
            for filter_config in config["filters"]:
                filter_type = filter_config.get("type")
                if filter_type == "level":
                    self.add_filter(
                        filters.LevelFilter(LogLevel[filter_config.get("level")])
                    )
                elif filter_type == "regex":
                    self.add_filter(filters.RegexFilter(filter_config.get("pattern")))
                elif filter_type == "time":
                    self.add_filter(
                        filters.TimeFilter(
                            start_time=filter_config.get("start_time"),
                            end_time=filter_config.get("end_time"),
                        )
                    )
                elif filter_type == "module":
                    self.add_filter(
                        filters.ModuleFilter(filter_config.get("module_name"))
                    )
                # elif filter_type == "composite":
                # self.add_filter(
                # filters.CompositeFilter(
                # filters=[
                #     ConfigLoader._create_filter(f)
                #     for f in filter_config.get("filters", [])
                # ],
                # mode=filter_config.get("mode", "AND"),
                # )
                # )

    def exception(
        self,
        message: str,
        exception: Optional[Exception] = None,
        level: LogLevel = LogLevel.ERROR,
        **kwargs: Any,
    ) -> None:
        """Логирует исключение с дополнительной информацией.

        Args:
            message (str): Сообщение об ошибке.
            exception (Optional[Exception]): Исключение.
            level (LogLevel): Уровень логирования.
            **kwargs: Дополнительные данные.
        """
        stack_trace = format_exc() if exception else None
        self(
            f"Исключение: {message}",
            level,
            stack_trace=stack_trace,
            exception_type=exception.__class__.__name__ if exception else None,
            **kwargs,
        )

    @contextmanager
    def catch_exceptions(
        self,
        message: str,
        level: LogLevel = LogLevel.ERROR,
        **kwargs: Any,
    ):
        """
        Контекстный менеджер для автоматического логирования исключений.

        Args:
            message (str): Сообщение для логирования.
            level (LogLevel): Уровень логирования.
            **kwargs: Дополнительные данные.
        """
        try:
            yield
        except Exception as e:
            self.exception(message, e, level, **kwargs)
            raise

    @contextmanager
    def context(
        self,
        message: str,
        level: LogLevel = LogLevel.INFO,
        start_message: Optional[str] = None,
        end_message: Optional[str] = None,
    ):
        """
        Контекстный менеджер для логирования начала и завершения блока кода.

        Args:
            message (str): Основное сообщение для логирования.
            level (LogLevel): Уровень логирования.
            start_message (Optional[str]): Сообщение в начале блока.
            end_message (Optional[str]): Сообщение в конце блока.
        """
        start_msg = start_message or f"Начало: {message}"
        end_msg = end_message or f"Завершение: {message}"

        self(start_msg, level)
        try:
            yield
        except Exception as e:
            self(f"Ошибка в блоке: {message} - {str(e)}", LogLevel.ERROR)
            raise
        finally:
            self(end_msg, level)

    def __repr__(self) -> str:
        return f"<class 'turbo_print.{self.__class__.__module__}.{self.__class__.__name__}[{self.name}]'>"

    def __str__(self) -> str:
        return self.name


def performance_metrics(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time()
        if iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)
        end_time = time()
        execution_time = end_time - start_time
        logger = TurboPrint.get_logger("performance")
        logger(
            f"Метод {func.__name__} выполнен за {execution_time:.4f} секунд",
            LogLevel.INFO,
        )
        return result

    return wrapper


tp = TurboPrint()
tp.add_handler(
    TimedRotatingFileHandler(
        Path("../logs/"), "test_{time}", compress=True, compress_format="rar"
    )
)
tp("message", LogLevel.WARNING)
