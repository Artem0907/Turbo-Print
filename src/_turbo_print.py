from typing import Optional as _Optional, TextIO as _TextIO
from sys import stdout as _default_stdout, stderr as _default_stderr
from datetime import datetime as _datetime

from ._types import LogLevel as _LogLevel, LogRecord as _LogRecord
from .formatters import (
    BaseFormatter as _BaseFormatter,
    DefaultFormatter as _DefaultFormatter,
)
from .handlers import (
    BaseHandler as _BaseHandler,
    StreamHandler as _StreamHandler,
)
from .filters import BaseFilter as _BaseFilter
from .inner_middlewares import BaseInnerMiddleware as _BaseInnerMiddleware
from .outer_middlewares import BaseOuterMiddleware as _BaseOuterMiddleware


__all__ = ("TurboPrint",)
_ROOT_LOGGER_NAME = "root"


class _TurboPrintLogMethods:
    _context: dict
    level: _LogLevel
    formatter: _BaseFormatter
    handlers: list[_BaseHandler]
    filters: list[_BaseFilter]
    inner_middlewares: list[_BaseInnerMiddleware]
    outer_middlewares: list[_BaseOuterMiddleware]

    def get_context(self) -> dict:
        return self._context.copy()

    def add_context(self, **context) -> None:
        self._context.update(**context)

    def get_level(self) -> _LogLevel:
        return self.level

    def set_level(self, level: _LogLevel) -> None:
        self.level = level

    def get_formatter(self) -> _BaseFormatter:
        return self.formatter

    def set_formatter(self, formatter: _BaseFormatter) -> None:
        self.formatter = formatter

    def get_handlers(self) -> list[_BaseHandler]:
        return self.handlers.copy()

    def add_formatter(self, handler: _BaseHandler) -> None:
        self.handlers.append(handler)

    def get_filters(self) -> list[_BaseFilter]:
        return self.filters.copy()

    def add_filter(self, filter: _BaseFilter) -> None:
        self.filters.append(filter)

    def get_inner_middlewares(self) -> list[_BaseInnerMiddleware]:
        return self.inner_middlewares.copy()

    def add_inner_middlewares(self, inner_middleware: _BaseInnerMiddleware):
        self.inner_middlewares.append(inner_middleware)

    def get_outer_middlewares(self) -> list[_BaseOuterMiddleware]:
        return self.outer_middlewares.copy()

    def add_outer_middlewares(self, outer_middleware: _BaseOuterMiddleware):
        self.outer_middlewares.append(outer_middleware)


class TurboPrint(_TurboPrintLogMethods):
    _context: dict = {}
    _root_logger: "TurboPrint"
    __register: list["TurboPrint"] = []

    @classmethod
    def __init_root_logger(cls):
        cls._root_logger = None  # type: ignore
        root_logger = cls(
            _ROOT_LOGGER_NAME,
            prefix=_ROOT_LOGGER_NAME,
            handlers=[_StreamHandler()],
        )
        root_logger.parent = None  # type: ignore
        cls._root_logger = root_logger

    def __init__(
        self,
        name: _Optional[str] = None,
        *,
        level: _LogLevel = _LogLevel.NOTSET,
        prefix: _Optional[str] = None,
        formatter: _Optional[_BaseFormatter] = None,
        handlers: _Optional[list[_BaseHandler]] = None,
        filters: _Optional[list[_BaseFilter]] = None,
        inner_middlewares: _Optional[list[_BaseInnerMiddleware]] = None,
        outer_middlewares: _Optional[list[_BaseOuterMiddleware]] = None,
        parent: _Optional["TurboPrint"] = None,
        stdout: _TextIO = _default_stdout,
        stderr: _TextIO = _default_stderr,
        **extra,
    ):
        if not hasattr(self, "_root_logger"):
            self.__init_root_logger()

        self.name = name.lower() if name else str(id(self))
        if self in self.__register:
            raise NameError(f"logger name={self.name} is registered")

        self.__register.append(self)

        self.level = level
        self.prefix: _Optional[str] = prefix
        self.formatter = formatter or _DefaultFormatter()
        self.handlers = handlers or []
        self.filters = filters or []
        self.inner_middlewares = inner_middlewares or []
        self.outer_middlewares = outer_middlewares or []
        self.parent: "TurboPrint" = parent or self._root_logger
        self.extra: dict = extra

        self.stdout = stdout
        self.stderr = stderr

    @classmethod
    def get_logger(cls, name: _Optional[str] = None, **kwargs) -> "TurboPrint":
        if not hasattr(cls, "_root_logger"):
            cls.__init_root_logger()
        if not name:
            return cls._root_logger
        return cls(name, **kwargs)

    def _start_handlers(self, record: _LogRecord):
        for inner_middleware in sorted(
            self.get_inner_middlewares(), key=lambda middleware: middleware.priority
        ):
            inner_middleware.handle(self, record)

        for handler in self.get_handlers():
            handler.handle(self, record)

        for outer_middleware in sorted(
            self.get_outer_middlewares(), key=lambda middleware: middleware.priority
        ):
            outer_middleware.handle(self, record)

    def __call__(self, message: str, level: _LogLevel = _LogLevel.NOTSET, **extra):
        record = _LogRecord(
            logger=self, message=message, level=level, datetime=_datetime.now()
        )
        if not all(map(lambda filter: filter.filter(record), self.get_filters())):
            return
        self._start_handlers(record)

    def __repr__(self) -> str:
        return f"<class {self.__class__.__name__} name={self.name} parent={self.parent.name if self.parent else None}>"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.name}]"

    def __copy__(self) -> "TurboPrint":
        return self

    copy = __copy__
