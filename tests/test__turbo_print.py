import unittest
from ..src.turbo_print import TurboPrint
from ..src.my_types import LogLevel

class TestTurboPrint(unittest.TestCase):
    def test_logger_creation(self) -> None:
        logger = TurboPrint.get_logger("test")
        self.assertEqual(logger.name, "test")

    def test_logging(self) -> None:
        logger = TurboPrint.get_logger("test")
        result = logger("Test message", LogLevel.INFO)
        self.assertIsNotNone(result)