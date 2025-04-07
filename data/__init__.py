from asyncio import to_thread as _to_thread
from atexit import register as _register_atexit
from collections.abc import Generator as _Generator
from contextlib import contextmanager as _contextmanager
from pathlib import Path as _Path
from typing import Any as _Any
from typing import ClassVar as _ClassVar
from typing import Literal as _Literal
from typing import Optional as _Optional
from typing import TextIO as _TextIO
from typing import Union as _Union

from aiofiles import open as _aio_open  # type: ignore

__all__ = ("FileManager", "TPStack")


class TPStack:
    """Stack for managing TurboPrint resources."""

    _stack: _ClassVar[list["TPStack"]] = []
    _is_closed: _ClassVar[bool] = False

    def __init__(self, *, priority: int = 0) -> None:
        """Initialize the stack.

        Args:
            priority: Priority of the element in the stack. Elements with higher priority
                     are processed first. Default is 0.

        Raises:
            RuntimeError: If the stack is already closed
        """  # noqa: E501
        if self._is_closed:
            raise RuntimeError("Stack is already closed")
        self.priority = priority
        self._stack.append(self)
        self._stack.sort(key=lambda x: x.priority, reverse=True)

    @classmethod
    def clear(cls) -> None:
        """Clear all resources from the stack."""
        cls._stack.clear()
        cls._is_closed = False

    @classmethod
    def close(cls) -> None:
        """Close and clear all resources from the stack."""
        cls.clear()
        cls._is_closed = True

    @classmethod
    def is_empty(cls) -> bool:
        """Check if the stack is empty.

        Returns:
            bool: True if the stack is empty, False otherwise
        """
        return len(cls._stack) == 0

    @classmethod
    def get_size(cls) -> int:
        """Get the current size of the stack.

        Returns:
            int: Number of elements in the stack
        """
        return len(cls._stack)

    @classmethod
    @_contextmanager
    def resource_manager(cls) -> _Generator[None, _Any]:
        """Context manager for managing resources.

        Yields:
            None
        """
        try:
            yield
        finally:
            cls.close()


class FileManager:
    """Manager for file operations."""

    def __init__(self, path: _Path | None = None) -> None:
        """Initialize the file manager.

        Args:
            path: Optional path to manage. If not specified, the default path will be used.
        """  # noqa: E501
        self._path = path or _Path.cwd()

    @_contextmanager
    async def open_file(
        self, filename: str, mode: _Literal["r", "rb", "w", "wb", "a"] = "r"
    ):
        """Open a file in the managed directory.

        Args:
            filename: Name of the file to open.
            mode: File opening mode.

        Yields:
            TextIO: Opened file object.
        """
        file_path = self._path / filename
        async with _aio_open(file_path, mode) as f:
            return f

    async def list_files(self, pattern: str = "*") -> list[_Path]:
        """List files in the managed directory.

        Args:
            pattern: Pattern for file search.

        Returns:
            List of paths to found files.
        """
        return list(self._path.glob(pattern))

    async def create_directory(self, name: str) -> _Path:
        """Create a new directory in the managed path.

        Args:
            name: Name of the directory to create.

        Returns:
            Path to the created directory.
        """
        new_dir = self._path / name
        await _to_thread(new_dir.mkdir, parents=True, exist_ok=True)
        return new_dir

    async def write(self, file_path: _Path, content: str) -> None:
        """Write content to a file.

        Args:
            file_path: Path to the file for writing.
            content: Content to write.
        """
        # Ensure the directory exists
        await _to_thread(file_path.parent.mkdir, parents=True, exist_ok=True)

        # Write the content
        async with _aio_open(file_path, "a") as f:
            await f.write(content)

    async def read_file(self, filename: str) -> str:
        """Read file contents.

        Args:
            filename: Name of the file to read.

        Returns:
            File contents as a string.
        """
        file_path = self._path / filename
        async with _aio_open(file_path) as f:
            return await f.read()

    def get_path(self) -> _Path:
        return self._path


_register_atexit(TPStack.close)
