from functools import wraps
import sys
from typing import ClassVar, Optional, Callable, Any, TextIO, TypeVar, Literal, cast
from datetime import datetime
from asyncio import AbstractEventLoop, get_running_loop, get_event_loop
from inspect import iscoroutinefunction
from contextvars import ContextVar

from colorama import Style

from src.my_types import LogLevel, TurboPrintOutput, LogRecord, TurboPrintConfig
from src.formatters import BaseFormatter, DefaultFormatter
from src.filters import BaseFilter
from src.handlers import BaseHandler, StreamHandler
from src.inner_middlewares import BaseInnerMiddleware
from src.outer_middlewares import BaseOuterMiddleware

__all__ = ["TurboPrint", "TurboPrintConfig"]
ROOT_LOGGER_NAME = "root"
_F = TypeVar("_F", bound=Callable[..., Any])
try:
    _DEFAULT_ASYNC_LOOP = get_running_loop()
except RuntimeError:
    _DEFAULT_ASYNC_LOOP = get_event_loop()


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
        """Фабричный метод для получения или создания логгера."""
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
    ) -> None:
        """Инициализация логгера."""
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
        self.filters = (
            ((self.parent.get_filters() + filters) if self.parent else filters)
            if filters
            else []
        )
        self.formatter = formatter
        self._children: list[TurboPrint] = []

        if self.name in TurboPrint._registry:
            stderr.write(f"ValueError: Логгер '{self.name}' уже существует" + "\n")
            stderr.flush()

        if self.parent:
            self.parent._add_child(self)

        TurboPrint._registry[self.name] = self

    def __call__(self, message: str, level: LogLevel = LogLevel.NOTSET, **kwargs: Any):
        """Основной метод логирования."""
        if not self.enabled or level < self.level:
            return False

        record = LogRecord(
            message=message,
            name=self.name,
            level=level,
            prefix=self.prefix,
            timestamp=datetime.now(),
            parent=self.parent,
            extra={**self._context.get(), **kwargs},
        )
        if any(not f.filter(record) for f in self.get_filters()):
            return False

        self.async_loop.run_until_complete(self._start_handlers(record))

        formatted = TurboPrintOutput(
            colored_console=self.formatter.format_colored(record),
            standard_file=self.formatter.format(record),
        )

        if self.parent and self.propagate:
            self.parent._propagate(record)

        return formatted

    def _add_child(self, child: "TurboPrint") -> None:
        """Добавление дочернего логгера."""
        self._children.append(child)

    def _propagate(self, record: LogRecord) -> None:
        """Распространение записи по иерархии."""
        new_record = record.copy()
        new_record["name"] = self.name
        new_record["prefix"] = self.prefix
        new_record["parent"] = self.parent

        if self.level <= new_record["level"]:
            self.async_loop.run_until_complete(self._start_handlers(new_record))

        if self.parent and self.propagate:
            self.parent._propagate(new_record)

    async def _start_handlers(self, record: LogRecord) -> None:
        """Запуск обработчиков с обработкой ошибок."""
        for handler in self.get_handlers():
            try:
                for inner_middleware in self.inner_middlewares:
                    await inner_middleware(
                        handler, self, record, self.stdout, self.stderr
                    )

                if iscoroutinefunction(handler.handle):
                    await handler.handle(self, record, self.stdout, self.stderr)
                else:
                    handler.handle(self, record, self.stdout, self.stderr)

                for outer_middleware in self.outer_middlewares:
                    await outer_middleware(
                        handler, self, record, self.stdout, self.stderr
                    )
            except Exception as e:
                self.stderr.write(f"Ошибка обработчика {handler}: {e}")
                self.stderr.flush()

    def set_context(self, **kwargs: Any) -> None:
        """Устанавливает контекст для логгера."""
        self._context.set(kwargs)

    def get_level(self) -> LogLevel:
        return self.level

    def set_level(self, level: LogLevel) -> None:
        self.level = level

    def get_filters(self) -> list[BaseFilter]:
        """Получение списка фильтров."""
        return self.parent.get_filters() + self.filters if self.parent else self.filters

    def add_filter(self, filter: BaseFilter) -> None:
        """Добавление фильтра."""
        self.filters.append(filter)

    def add_handler(self, handler: BaseHandler) -> None:
        """Добавление обработчика."""
        self.handlers.append(handler)

    def get_handlers(self) -> list[BaseHandler]:
        """Получение списка обработчиков."""
        return (
            self.parent.get_handlers() + self.handlers
            if self.parent and self.propagate
            else self.handlers
        )

    def set_formatter(self, formatter: BaseFormatter) -> None:
        """Изменение форматировщика."""
        self.formatter = formatter

    def exception(self, **log_params: Any) -> Callable[[_F], _F]:
        """Декоратор для логирования исключений."""

        def get_func(func: _F) -> _F:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as exception:
                    exc_name = exception.__class__.__name__
                    exc_file = f"{func.__code__.co_filename.replace("\\", "/")}:{func.__code__.co_firstlineno}"
                    exception_message = f'Исключение {exc_name} в "{exc_file}" [{func.__name__}]: {str(exception)}'
                    self(exception_message, LogLevel.CRITICAL, **log_params)
                    self.stderr.write(
                        LogLevel.CRITICAL.color + exception_message + Style.RESET_ALL
                    )
                    exit(1)

            return cast(_F, wrapper)

        return get_func

    def __repr__(self) -> str:
        return f"<class 'turbo_print.{self.__class__.__module__}.{self.__class__.__name__}[{self.name}]'>"

    def __str__(self) -> str:
        return self.name
