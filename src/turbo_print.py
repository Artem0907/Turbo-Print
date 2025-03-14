from functools import wraps
from typing import ClassVar, Optional, Callable, Any, TypeVar, Literal, cast
from datetime import datetime

from src.my_types import LogLevel, TurboPrintOutput, LogRecord
from src.formatters import BaseFormatter, DefaultFormatter
from src.filters import BaseFilter
from src.handlers import BaseHandler, StreamHandler

__all__ = ["TurboPrint"]
ROOT_LOGGER_NAME = "root"
_F = TypeVar("_F", bound=Callable[..., Any])


class TurboPrint:
    """Иерархическая система логирования с расширенными возможностями."""

    _registry: ClassVar[dict[str, "TurboPrint"]] = {}
    _root_logger: ClassVar["TurboPrint"]

    @classmethod
    def _init_root_logger(cls) -> None:
        """Инициализация корневого логгера."""
        cls._root_logger = None  # type: ignore
        root = cls(
            ROOT_LOGGER_NAME,
            prefix="ROOT",
            level=LogLevel.INFO,  # Исправлено с LOG на INFO
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
        formatter: BaseFormatter = DefaultFormatter(),
    ) -> None:
        """Инициализация логгера."""
        if not hasattr(TurboPrint, "_root_logger"):
            TurboPrint._init_root_logger()

        self.name = name or str(id(self))
        self.enabled = enabled
        self.prefix = prefix
        self.level = level
        self.parent = parent if parent else self._root_logger
        self.propagate = propagate
        self.handlers = handlers or []
        self.filters = (
            ((self.parent.get_filters() + filters) if self.parent else filters)
            if filters
            else []
        )
        self.formatter = formatter
        self._children: list[TurboPrint] = []

        if self.name in TurboPrint._registry:
            raise ValueError(f"Логгер '{self.name}' уже существует")

        if self.parent:
            self.parent._add_child(self)

        TurboPrint._registry[self.name] = self

    def __call__(
        self, message: str, level: LogLevel = LogLevel.NOTSET, **kwargs: Any
    ) -> TurboPrintOutput | Literal[False]:
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
            extra=kwargs,
        )
        if any(not f.filter(record) for f in self.get_filters()):
            return False

        formatted = TurboPrintOutput(
            colored_console=self.formatter.format_colored(record),
            standard_file=self.formatter.format(record),
        )

        self._start_handlers(record, formatted)

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
            formatted = TurboPrintOutput(
                colored_console=self.formatter.format_colored(new_record),
                standard_file=self.formatter.format(new_record),
            )
            self._start_handlers(new_record, formatted)

        if self.parent and self.propagate:
            self.parent._propagate(new_record)

    def _start_handlers(self, record: LogRecord, formatted: TurboPrintOutput) -> None:
        """Запуск обработчиков."""
        for handler in self.get_handlers():
            try:
                handler.handle(record, formatted)
            except Exception as e:
                print(f"Ошибка обработчика {handler}: {e}")

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
                except Exception as e:
                    self(
                        f"Исключение в {func.__name__}: {str(e)}",
                        LogLevel.CRITICAL,
                        **log_params,
                    )
                    raise

            return cast(_F, wrapper)

        return get_func

    def __repr__(self) -> str:
        return f"<class 'turbo_print.{self.__class__.__module__}.{self.__class__.__name__}[{self.name}]'>"

    def __str__(self) -> str:
        return self.name
