from unittest.mock import MagicMock as _MagicMock, patch as _patch
from io import StringIO as _StringIO
from contextlib import redirect_stdout as _redirect_stdout

from tests.test__main import MainTestCase as _MainTestCase
from src.turbo_print import TurboPrint as _TurboPrint

__all__ = ["TurboPrintTestCase"]


class TurboPrintTestCase(_MainTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()
