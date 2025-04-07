from typing import Optional as _Optional, TextIO as _TextIO
from sys import stdout as _default_stdout, stderr as _default_stderr
from datetime import datetime as _datetime
from asyncio import (
    get_running_loop as _get_running_async_loop,
    get_event_loop as _get_async_loop,
)

from nest_asyncio import apply as _async_loop_apply

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
    _context: dict[str, object]
    handlers: list[_BaseHandler]
    filters: list[_BaseFilter]
    inner_middlewares: list[_BaseInnerMiddleware]
    outer_middlewares: list[_BaseOuterMiddleware]

    def get_context(self) -> dict[str, object]:
        return self._context.copy()

    def add_context(self, **context: object) -> None:
        self._context.update(**context)

    @property
    def level(self) -> _LogLevel:
        return self._level

    @level.setter
    def level(self, value: _LogLevel) -> None:
        self._level = value

    @property
    def formatter(self) -> _BaseFormatter:
        return self._formatter

    @formatter.setter
    def formatter(self, value: _BaseFormatter) -> None:
        self._formatter = value

    def get_handlers(self) -> list[_BaseHandler]:
        return self.handlers.copy()

    def add_handler(self, handler: _BaseHandler) -> None:
        self.handlers.append(handler)

    def get_filters(self) -> list[_BaseFilter]:
        return self.filters.copy()

    def add_filter(self, filter: _BaseFilter) -> None:
        self.filters.append(filter)

    def get_inner_middlewares(self) -> list[_BaseInnerMiddleware]:
        return self.inner_middlewares.copy()

    def add_inner_middleware(self, middleware: _BaseInnerMiddleware) -> None:
        self.inner_middlewares.append(middleware)

    def get_outer_middlewares(self) -> list[_BaseOuterMiddleware]:
        return self.outer_middlewares.copy()

    def add_outer_middleware(self, middleware: _BaseOuterMiddleware) -> None:
        self.outer_middlewares.append(middleware)


class TurboPrint(_TurboPrintLogMethods):
    _context: dict[str, object] = {}
    _root_logger: "TurboPrint"
    __register: list["TurboPrint"] = []

    @classmethod
    def __init_root_logger(cls) -> None:
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
        **extra: object,
    ) -> None:
        if not hasattr(self, "_root_logger"):
            self.__init_root_logger()

        self.name = (name or str(id(self))).lower()
        if self in self.__register:
            raise NameError(f"logger name={self.name} is registered")

        self.__register.append(self)

        self.level = level
        self.prefix = prefix
        self.formatter = formatter or _DefaultFormatter()
        self.handlers = handlers or []
        self.filters = filters or []
        self.inner_middlewares = inner_middlewares or []
        self.outer_middlewares = outer_middlewares or []
        self.parent = parent or self._root_logger
        self.extra = extra
        self.stdout = stdout
        self.stderr = stderr
        self.copy = self.__copy__

        try:
            self.async_loop = _get_running_async_loop()
        except RuntimeError:
            self.async_loop = _get_async_loop()

    @classmethod
    def get_logger(cls, name: _Optional[str] = None, **kwargs: object) -> "TurboPrint":
        if not hasattr(cls, "_root_logger"):
            cls.__init_root_logger()
        if not name:
            return cls._root_logger
        return cls(name, **kwargs)

    async def _start_handlers(self, record: _LogRecord) -> None:
        sorted_inner_middlewares = sorted(
            self.get_inner_middlewares(), key=lambda middleware: middleware.priority
        )
        for inner_middleware in sorted_inner_middlewares:
            await inner_middleware.handle(self, record)

        for handler in self.get_handlers():
            await handler.handle(self, record)

        sorted_outer_middlewares = sorted(
            self.get_outer_middlewares(), key=lambda middleware: middleware.priority
        )
        for outer_middleware in sorted_outer_middlewares:
            await outer_middleware.handle(self, record)

    def __call__(self, message: str, level: _LogLevel = _LogLevel.NOTSET, **extra: object) -> None:
        record = _LogRecord(
            logger=self, message=message, level=level, datetime=_datetime.now()
        )
        if not all(filter.filter(record) for filter in self.get_filters()):
            return

        _async_loop_apply()
        self.async_loop.run_until_complete(self._start_handlers(record))

    def __repr__(self) -> str:
        parent_name = self.parent.name if self.parent else None
        return (
            f"<class {self.__class__.__name__} name={self.name} parent={parent_name}>"
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.name}]"

    def __copy__(self) -> "TurboPrint":
        return self
