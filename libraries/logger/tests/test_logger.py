import logging
import unittest
from unittest import mock

from logger.fplogger import _get_environment, setup_log


class TestSetupLog(unittest.TestCase):

    def test_setup_log_without_email_handler(self):
        self._init_handlers()

        setup_log("demo-app")

        logger = logging.getLogger()

        self.assertEqual(type(logger.handlers[0]).__name__, "StreamHandler")
        self.assertEqual(type(logger.handlers[1]).__name__, "RotatingFileHandler")

    def test_setup_log_with_email_handler(self):
        self._init_handlers()

        setup_log("demo-app", alert_to="chakim@freepoint.com")

        logger = logging.getLogger()

        self.assertEqual(type(logger.handlers[0]).__name__, "StreamHandler")
        self.assertEqual(type(logger.handlers[1]).__name__, "RotatingFileHandler")
        self.assertEqual(type(logger.handlers[2]).__name__, "SMTPHandler")

    @mock.patch("socket.gethostname")
    def test_get_environment(self, mock_gethostname):

        mock_gethostname.return_value = "uk-w1-52-01"
        actual = _get_environment()
        self.assertEqual(actual, "Development")

        mock_gethostname.return_value = "tst-scr-app-01"
        actual = _get_environment()
        self.assertEqual(actual, "Test")

        mock_gethostname.return_value = "PRD-scr-app-01"
        actual = _get_environment()
        self.assertEqual(actual, "Production")

    def _init_handlers(self):
        # Clean up handlers
        logging.basicConfig(handlers=[])