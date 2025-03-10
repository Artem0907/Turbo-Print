from unittest.mock import MagicMock as _MagicMock, patch as _patch
from io import StringIO as _StringIO
from contextlib import redirect_stdout as _redirect_stdout

from tests.test__main import MainTestCase as _MainTestCase
from src.my_types import LogLevel as _LogLevel

__all__ = [
    "MyTypesTestCase",
    "Test_LogLevels",
    "Test_LogLevelsMethods",
]


class MyTypesTestCase(_MainTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()


class Test_LogLevels(MyTypesTestCase):
    @_patch("sys.stdout", new_callable=_StringIO)
    @_patch("builtins.open", create=True)
    def test_filter(self, mock_open: _MagicMock, mock_stdout: _StringIO) -> None: ...


class Test_LogLevelsMethods(MyTypesTestCase):
    @_patch("sys.stdout", new_callable=_StringIO)
    @_patch("builtins.open", create=True)
    def test_filter(self, mock_open: _MagicMock, mock_stdout: _StringIO) -> None: ...
