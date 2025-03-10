from unittest.mock import MagicMock as _MagicMock, patch as _patch
from io import StringIO as _StringIO
from datetime import time as _time, datetime as _datetime
from contextlib import redirect_stdout as _redirect_stdout

from tests.test__main import MainTestCase as _MainTestCase
from src.my_types import LogLevel as _LogLevel, LogRecord as _LogRecord
from src.filters import (
    LevelFilter as _LevelFilter,
    RegexFilter as _RegexFilter,
    TimeFilter as _TimeFilter,
)

__all__ = [
    "FiltersTestCase",
    "Test_LevelFilter",
    "Test_RegexFilter",
    "Test_TimeFilter",
]


class FiltersTestCase(_MainTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()


class Test_LevelFilter(FiltersTestCase):
    @_patch("sys.stdout", new_callable=_StringIO)
    @_patch("builtins.open", create=True)
    def test_filter(self, mock_open: _MagicMock, mock_stdout: _StringIO) -> None:
        record: _LogRecord = {"level": _LogLevel.LOG}  # type: ignore

        self.assertTrue(_LevelFilter(_LogLevel.DEBUG).filter(record))
        self.assertTrue(_LevelFilter(_LogLevel.LOG).filter(record))
        self.assertFalse(_LevelFilter(_LogLevel.ERROR).filter(record))


class Test_RegexFilter(FiltersTestCase):
    @_patch("sys.stdout", new_callable=_StringIO)
    @_patch("builtins.open", create=True)
    def test_filter(self, mock_open: _MagicMock, mock_stdout: _StringIO) -> None:
        record: _LogRecord = {"message": "test EROR message"} # type: ignore
        self.assertFalse(_RegexFilter(r"E[R]ROR", invert = False).filter(record))
        self.assertTrue(_RegexFilter(r"E[R]ROR", invert =True).filter(record))


class Test_TimeFilter(FiltersTestCase):
    @_patch("sys.stdout", new_callable=_StringIO)
    @_patch("builtins.open", create=True)
    def test_filter(self, mock_open: _MagicMock, mock_stdout: _StringIO) -> None:
        start_time = _time(10, 0, 0, 0)
        end_time = _time(19, 0, 0, 0)
        time_true = _datetime(2017, 6, 24, 15, 0, 0, 0)
        time_false = _datetime(2017, 6, 24, 6, 0, 0, 0)

        self.assertTrue(
            _TimeFilter(start_time, end_time).filter(
                {"date_time": time_true}  # type:  ignore
            )
        )
        self.assertFalse(
            _TimeFilter(start_time, end_time).filter(
                {"date_time": time_false}  # type:  ignore
            )
        )
