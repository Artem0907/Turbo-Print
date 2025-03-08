from functools import wraps
from typing import (
    ClassVar as _ClassVar,
    Optional as _Optional,
    Callable as _Callable,
    Any as _Any,
    TypeVar as _TypeVar,
    cast as _cast,
    Literal as _Literal,
)
from sys import stderr as _stderr
from datetime import datetime as _datetime

from src.types import (
    LogLevel as _LogLevel,
    TurboPrintOutput as _TurboPrintOutput,
    LogRecord as _LogRecord,
)
from src.formatters import (
    BaseFormatter as _BaseFormatter,
    DefaultFormatter as _DefaultFormatter,
)
from src.filters import BaseFilter as _BaseFilter
from src.handlers import BaseHandler as _BaseHandler, StreamHandler as _StreamHandler

__all__ = ["TurboPrint"]
ROOT_LOGGER_NAME = "root"
_F = _TypeVar("_F", bound=_Callable[..., _Any])


class TurboPrint:
    """Иерархическая система логгирования с расширенными возможностями"""

    _registry: _ClassVar[dict[str, "TurboPrint"]] = {}
    _root_logger: _ClassVar["TurboPrint"]

    @classmethod
    def _init_root_logger(cls) -> None:
        """Инициализация корневого логгера"""
        root = cls.__new__(cls)
        root.name = ROOT_LOGGER_NAME
        root.parent = None
        root._children = []
        root.prefix = "ROOT"
        root.enabled = True
        root.level = _LogLevel.LOG
        root.filters = []
        root.handlers = [_StreamHandler()]
        root.formatter = _DefaultFormatter()
        root.propagate = False

        cls._root_logger = root
        cls._registry[ROOT_LOGGER_NAME] = root

    @classmethod
    def get_logger(cls, name: _Optional[str] = None, **kwargs: _Any) -> "TurboPrint":
        """Фабричный метод для получения или создания логгера"""
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
        *,
        name: _Optional[str] = None,
        enabled: bool = True,
        prefix: _Optional[str] = None,
        level: _LogLevel = _LogLevel.NOTSET,
        parent: _Optional["TurboPrint"] = None,
        propagate: bool = True,
        handlers: list[_BaseHandler] = [],
        filters: list[_BaseFilter] = [],
        formatter: _BaseFormatter = _DefaultFormatter(),
    ) -> None:
        """Инициализирует экземпляр логгера TurboPrint.

        Args:
            name (Optional[str]): Уникальное имя логгера. Если не указано,
                генерируется автоматически через id(self). По умолчанию None.
            enabled (bool): Флаг активности логгера. Если False, логгер игнорирует
                сообщения. По умолчанию True.
            prefix (Optional[str]): Префикс для всех сообщений логгера.
                По умолчанию None.
            level (LogLevel): Минимальный уровень логирования (из перечисления).
                По умолчанию NOTSET (принимает все уровни).
            parent (Optional[TurboPrint]): Родительский логгер для создания иерархии.
                По умолчанию None.
            propagate (bool): Передавать ли сообщения родительским логгерам.
                По умолчанию True.
            handlers (list[BaseHandler]): Список обработчиков сообщений
                (например, вывод в консоль/файл). По умолчанию [].
            filters (list[BaseFilter]): Список фильтров для управления
                обработкой сообщений. По умолчанию [].
            formatter (BaseFormatter): Форматировщик для преобразования
                сообщений в строку. По умолчанию DefaultFormatter().

        Raises:
            ValueError: Если логгер с указанным именем уже существует в реестре.

        Notes:
            - При создании автоматически регистрируется в общем реестре TurboPrint.
            - Для использования иерархии логгеров укажите parent.
            - Изменяемые аргументы (handlers/filters) передаются по ссылке.
        """
        self._init_root_logger()

        self.name = name or str(id(self))
        self.enabled = enabled
        self.prefix = prefix
        self.level = level
        self.parent = parent if parent else self._root_logger
        self.propagate = propagate
        self.handlers = handlers
        self.filters = filters
        self.formatter = formatter
        self._children: list[TurboPrint] = []

        if self.name in TurboPrint._registry:
            raise ValueError(f"Логгер '{self.name}' уже существует")

        if self.parent:
            self.parent._add_child(self)

        TurboPrint._registry[self.name] = self

    def __call__(
        self, message: str, level: _LogLevel = _LogLevel.NOTSET, **kwargs: _Any
    ) -> _TurboPrintOutput | _Literal[False]:
        """Основной метлд логирования"""
        if not self.enabled or level.value < self.level.value:
            return False

        record = _LogRecord(
            message=message,
            level=level,
            prefix=self.prefix,
            date_time=_datetime.now(),
            parent=self.parent,
            extra=kwargs,
        )
        if not all(f.filter(record) for f in self.filters):
            return False

        formatted = _TurboPrintOutput(
            colored_console=self.formatter.format_colored(record),
            standard_file=self.formatter.format(record),
        )

        for handler in self.handlers:
            try:
                handler.handle(record, formatted)
            except Exception as e:
                _stderr.write(
                    f"Ошибка обработчика {handler.__class__.__name__}: {str(e)}\n"
                )

        if self.propagate and self.parent:
            self.parent._propagate(record, formatted)

        return formatted

    def _add_child(self, child: "TurboPrint") -> None:
        """Добавление дочернего логгера"""
        self._children.append(child)

    def _propagate(self, record: _LogRecord, formatted: _TurboPrintOutput) -> None:
        """Распространение записи по иерархии"""
        if self.level.value <= record["level"].value and all(
            f.filter(record) for f in self.filters
        ):
            for handler in self.handlers:
                try:
                    handler.handle(record, formatted)
                except Exception as e:
                    _stderr.write(
                        f"Ошибка обработчика {handler.__class__.__name__}: {str(e)}\n"
                    )

        if self.propagate and self.parent is not None:
            self.parent._propagate(record, formatted)

    def add_filter(self, filter: _BaseFilter) -> None:
        """Добавление фильтра"""
        self.filters.append(filter)

    def add_handler(self, handler: _BaseHandler) -> None:
        """Добавление обработчика"""
        self.handlers.append(handler)

    def set_formatter(self, formatter: _BaseFormatter) -> None:
        """Изменение форматировщика"""
        self.formatter = formatter

    def exception(self, **log_params) -> _Callable[[_F], _F]:
        """Декоратор для автоматического логирования исключений"""

        def get_func(func: _F) -> _F:
            @wraps(func)
            def wrapper(*args: _Any, **kwargs: _Any) -> _Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self(
                        f"Исключение в {func.__name__}: {str(e)}",
                        _LogLevel.CRITICAL,
                        **log_params,
                    )
                    return

            return _cast(_F, wrapper)

        return get_func

    def __repr__(self) -> str:
        return f"<TurboPrint: {self.name}>"
