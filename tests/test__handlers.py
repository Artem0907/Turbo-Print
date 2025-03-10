from unittest.mock import MagicMock as _MagicMock, patch as _patch
from io import StringIO as _StringIO
from contextlib import redirect_stdout as _redirect_stdout

from tests.test__main import MainTestCase as _MainTestCase
from src.handlers import (
    FileHandler as _FileHandler,
    StreamHandler as _StreamHandler,
    TelegramHandler as _TelegramHandler,
)

__all__ = [
    "HandlersTestCase",
    "Test_FileHandler",
    "Test_StreamHandler",
    "Test_TimeFilter",
]


class HandlersTestCase(_MainTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()


class Test_FileHandler(HandlersTestCase):
    @_patch("sys.stdout", new_callable=_StringIO)
    @_patch("builtins.open", create=True)
    def test_filter(self, mock_open: _MagicMock, mock_stdout: _StringIO) -> None: ...


class Test_StreamHandler(HandlersTestCase):
    @_patch("sys.stdout", new_callable=_StringIO)
    @_patch("builtins.open", create=True)
    def test_filter(self, mock_open: _MagicMock, mock_stdout: _StringIO) -> None: ...


class Test_TimeFilter(HandlersTestCase):
    @_patch("sys.stdout", new_callable=_StringIO)
    @_patch("builtins.open", create=True)
    def test_filter(self, mock_open: _MagicMock, mock_stdout: _StringIO) -> None: ...
