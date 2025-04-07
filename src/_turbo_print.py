# Standard library imports
from asyncio import (
    get_event_loop as _get_async_loop,
)
from asyncio import (
    get_running_loop as _get_running_async_loop,
)
from datetime import datetime as _datetime
from sys import stderr as _default_stderr
from sys import stdout as _default_stdout
from typing import Any as _Any
from typing import Optional as _Optional
from typing import TextIO as _TextIO

# Third-party imports
from nest_asyncio import apply as _async_loop_apply  # type: ignore

# Local imports
from ._types import LogLevel as _LogLevel
from ._types import LogRecord as _LogRecord
from .filters import BaseFilter as _BaseFilter
from .formatters import (
    BaseFormatter as _BaseFormatter,
)
from .formatters import (
    DefaultFormatter as _DefaultFormatter,
)
from .handlers import (
    BaseHandler as _BaseHandler,
)
from .handlers import (
    StreamHandler as _StreamHandler,
)
from .inner_middlewares import BaseInnerMiddleware as _BaseInnerMiddleware
from .outer_middlewares import BaseOuterMiddleware as _BaseOuterMiddleware

__all__ = ("TurboPrint",)
_ROOT_LOGGER_NAME = "root"


class _TurboPrintLogMethods:
    """Base class with logging methods for TurboPrint."""

    _context: dict[str, object]
    handlers: list[_BaseHandler]
    filters: list[_BaseFilter]
    inner_middlewares: list[_BaseInnerMiddleware]
    outer_middlewares: list[_BaseOuterMiddleware]

    def get_context(self) -> dict[str, object]:
        """Get a copy of the current logging context."""
        return self._context.copy()

    def add_context(self, **context: object) -> None:
        """Add new values to the logging context."""
        self._context.update(**context)

    @property
    def level(self) -> _LogLevel:
        """Get the current logging level."""
        return self._level

    @level.setter
    def level(self, value: _LogLevel) -> None:
        """Set a new logging level."""
        self._level = value

    @property
    def formatter(self) -> _BaseFormatter:
        """Get the current formatter."""
        return self._formatter

    @formatter.setter
    def formatter(self, value: _BaseFormatter) -> None:
        """Set a new formatter."""
        self._formatter = value

    def get_handlers(self) -> list[_BaseHandler]:
        """Get the list of log handlers."""
        return self.handlers.copy()

    def add_handler(self, handler: _BaseHandler) -> None:
        """Add a new log handler."""
        self.handlers.append(handler)

    def get_filters(self) -> list[_BaseFilter]:
        """Get the list of log filters."""
        return self.filters.copy()

    def add_filter(self, filter: _BaseFilter) -> None:
        """Add a new log filter."""
        self.filters.append(filter)

    def get_inner_middlewares(self) -> list[_BaseInnerMiddleware]:
        """Get the list of inner middlewares."""
        return self.inner_middlewares.copy()

    def add_inner_middleware(self, middleware: _BaseInnerMiddleware) -> None:
        """Add a new inner middleware."""
        self.inner_middlewares.append(middleware)

    def get_outer_middlewares(self) -> list[_BaseOuterMiddleware]:
        """Get the list of outer middlewares."""
        return self.outer_middlewares.copy()

    def add_outer_middleware(self, middleware: _BaseOuterMiddleware) -> None:
        """Add a new outer middleware."""
        self.outer_middlewares.append(middleware)


class TurboPrint(_TurboPrintLogMethods):
    """Main class for logging with extended capabilities."""

    _context: dict[str, object] = {}  # noqa: RUF012
    _root_logger: "TurboPrint"
    __register: list["TurboPrint"] = []  # noqa: RUF012

    @classmethod
    def __init_root_logger(cls) -> None:
        """Initialize the root logger."""
        cls._root_logger = None  # type: ignore
        root_logger = cls(
            _ROOT_LOGGER_NAME,
            prefix=_ROOT_LOGGER_NAME,
            handlers=[_StreamHandler()],
        )
        root_logger.parent = None  # type: ignore
        cls._root_logger = root_logger

    def __init__(  # noqa: PLR0913
        self,
        name: str | None = None,
        *,
        level: _LogLevel = _LogLevel.NOTSET,
        prefix: str | None = None,
        formatter: _BaseFormatter | None = None,
        handlers: list[_BaseHandler] | None = None,
        filters: list[_BaseFilter] | None = None,
        inner_middlewares: list[_BaseInnerMiddleware] | None = None,
        outer_middlewares: list[_BaseOuterMiddleware] | None = None,
        parent: _Optional["TurboPrint"] = None,
        stdout: _TextIO = _default_stdout,
        stderr: _TextIO = _default_stderr,
        **extra: object,
    ) -> None:
        """Initialize the logger.

        Args:
            name: Logger name
            level: Logging level
            prefix: Prefix for messages
            formatter: Formatter for messages
            handlers: Log handlers
            filters: Log filters
            inner_middlewares: Inner middlewares
            outer_middlewares: Outer middlewares
            parent: Parent logger
            stdout: Stream for standard output
            stderr: Stream for error output
            **extra: Additional parameters
        """
        if not hasattr(self, "_root_logger"):
            self.__init_root_logger()

        self.name = (name or str(id(self))).lower()
        if self in self.__register:
            raise NameError(
                f"Logger with name {self.name} is already registered"
            )

        self.__register.append(self)

        self.level = level
        self.prefix = prefix or self.name
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
    def get_logger(
        cls, name: str | None = None, **kwargs: _Any
    ) -> "TurboPrint":
        """Get a logger instance.

        Args:
            name: Logger name
            **kwargs: Additional parameters

        Returns:
            Logger instance
        """
        if not hasattr(cls, "_root_logger"):
            cls.__init_root_logger()
        if not name:
            return cls._root_logger
        return cls(name, **kwargs)

    async def _start_handlers(self, record: _LogRecord) -> None:
        """Start log handlers.

        Args:
            record: Log record to process
        """
        try:
            sorted_inner_middlewares = sorted(
                self.get_inner_middlewares(),
                key=lambda middleware: middleware.priority,
            )
            for inner_middleware in sorted_inner_middlewares:
                await inner_middleware.handle(self, record)

            for handler in self.get_handlers():
                await handler.handle(self, record)

            sorted_outer_middlewares = sorted(
                self.get_outer_middlewares(),
                key=lambda middleware: middleware.priority,
            )
            for outer_middleware in sorted_outer_middlewares:
                await outer_middleware.handle(self, record)
        except Exception as e:
            # Log the error but don't let it propagate
            error_message = f"Error in handler chain: {e!s}"
            await self.alog(error_message, level=_LogLevel.ERROR)

    async def alog(
        self, message: str, level: _LogLevel = _LogLevel.NOTSET, **extra: object
    ) -> None:
        """Asynchronous logging of a message.

        Args:
            message: Message text
            level: Log level
            **extra: Additional parameters
        """
        try:
            record = _LogRecord(
                logger=self,
                message=message,
                level=level,
                datetime=_datetime.now(),
            )
            if not all(
                [await filter.filter(record) for filter in self.get_filters()]
            ):
                return

            await self._start_handlers(record)
        except Exception as e:
            # Log the error but don't let it propagate
            error_message = f"Error in async logging: {e!s}"
            await self.alog(error_message, level=_LogLevel.ERROR)

    def __call__(
        self, message: str, level: _LogLevel = _LogLevel.NOTSET, **extra: object
    ) -> None:
        """Synchronous logging of a message.

        Args:
            message: Message text
            level: Log level
            **extra: Additional parameters
        """
        try:
            record = _LogRecord(
                logger=self,
                message=message,
                level=level,
                datetime=_datetime.now(),
            )

            # Run filter checks synchronously
            filter_results = []
            for filter in self.get_filters():
                try:
                    result = self.async_loop.run_until_complete(
                        filter.filter(record)
                    )
                    filter_results.append(result)
                except Exception as e:
                    # If a filter fails, treat it as False
                    filter_results.append(False)
                    error_message = f"Filter error: {e!s}"
                    self.async_loop.run_until_complete(
                        self.alog(error_message, level=_LogLevel.ERROR)
                    )

            if not all(filter_results):
                return

            _async_loop_apply()
            self.async_loop.run_until_complete(self._start_handlers(record))
        except Exception as e:
            # Log the error but don't let it propagate
            error_message = f"Error in sync logging: {e!s}"
            self.async_loop.run_until_complete(
                self.alog(error_message, level=_LogLevel.ERROR)
            )

    def __repr__(self) -> str:
        """String representation of the logger for debugging."""
        parent_name = self.parent.name if self.parent else None
        class_name = self.__class__.__name__
        return f"<class {class_name} name={self.name} parent={parent_name}>"

    def __str__(self) -> str:
        """String representation of the logger."""
        class_name = self.__class__.__name__
        return f"{class_name}[{self.name}]"

    def __copy__(self) -> "TurboPrint":
        """Create a copy of the logger."""
        return self
