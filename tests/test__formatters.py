import unittest
from datetime import datetime
from src.formatters import DefaultFormatter, JSONFormatter
from src.my_types import LogLevel, LogRecord

class TestDefaultFormatter(unittest.TestCase):
    def test_format(self) -> None:
        formatter = DefaultFormatter()
        record: LogRecord = {
            "message": "Test",
            "level": LogLevel.INFO,
            "name": "test",
            "prefix": "TEST",
            "timestamp": datetime.now(),
            "parent": None,
            "extra": {},
        }
        formatted = formatter.format(record)
        self.assertIn("INFO", formatted)

class TestJSONFormatter(unittest.TestCase):
    def test_format(self) -> None:
        formatter = JSONFormatter()
        record: LogRecord = {
            "message": "Test",
            "level": LogLevel.INFO,
            "name": "test",
            "prefix": "TEST",
            "timestamp": datetime.now(),
            "parent": None,
            "extra": {},
        }
        formatted = formatter.format(record)
        self.assertIn('"level": "INFO"', formatted)