from unittest.mock import MagicMock as _MagicMock, patch as _patch
from io import StringIO as _StringIO
from contextlib import redirect_stdout as _redirect_stdout
from datetime import datetime as _datetime
from colorama import Style as _Style
from ujson import dumps as _dumps

from tests.test__main import MainTestCase as _MainTestCase
from src.my_types import LogLevel as _LogLevel, LogRecord as _LogRecord
from src.formatters import (
    DefaultFormatter as _DefaultFormatter,
    JSONFormatter as _JSONFormatter,
)

__all__ = [
    "FormattersTestCase",
    "Test_DefaultFormatter",
    "Test_JsonFormatter",
]


class FormattersTestCase(_MainTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()


class Test_DefaultFormatter(FormattersTestCase):
    @_patch("sys.stdout", new_callable=_StringIO)
    @_patch("builtins.open", create=True)
    def test_filter(self, mock_open: _MagicMock, mock_stdout: _StringIO) -> None:
        format = "{prefix}[{level_value}]: {message}"
        record = _LogRecord(
            message="MESSAGE",
            name="name",
            level=_LogLevel.DEBUG,
            prefix="PREFIX",
            date_time=_datetime.now(),
            parent=None,
            extra={},
        )

        self.assertEqual(
            format.format(**record, level_value=record["level"].value),
            _DefaultFormatter(format).format(record),
        )
        self.assertEqual(
            record["level"].color
            + format.format(**record, level_value=record["level"].value)
            + _Style.RESET_ALL,
            _DefaultFormatter(format).format_colored(record),
        )


class Test_JsonFormatter(FormattersTestCase):
    @_patch("sys.stdout", new_callable=_StringIO)
    @_patch("builtins.open", create=True)
    def test_filter(self, mock_open: _MagicMock, mock_stdout: _StringIO) -> None:
        record = _LogRecord(
            message="MESSAGE",
            name="name",
            level=_LogLevel.DEBUG,
            prefix="PREFIX",
            date_time=_datetime.now(),
            parent=None,
            extra={},
        )
        log_data = {
            "message": record["message"],
            "name": record["name"],
            "level": record["level"].name,
            "prefix": record["prefix"] or record["name"],
            "date_time": record["date_time"].isoformat(),
            "parent": repr(record["parent"]),
        }

        self.assertEqual(
            _dumps(log_data, ensure_ascii=False), _JSONFormatter().format(record)
        )
        self.assertEqual(
            _dumps(log_data, ensure_ascii=False),
            _JSONFormatter().format_colored(record),
        )
