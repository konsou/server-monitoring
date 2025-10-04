import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch

import _smart
import _smart_types
from _smart_types import DeviceTestResult

from tests.test_data import (
    INFO_DICT_STATUS_OK,
    INFO_DICT_STATUS_FAIL,
    INFO_DICT_STATUS_MISSING,
    INFO_DICT_STATUS_BLOCK_MISSING,
)


def disable_logging():
    logger = logging.getLogger("server-monitoring")
    logger = MagicMock()


class TestSmart(TestCase):
    def test_status_passed(self):
        res = _smart.status_passed(INFO_DICT_STATUS_OK)
        self.assertEqual(res, True)

    def test_status_failed(self):
        res = _smart.status_passed(INFO_DICT_STATUS_FAIL)
        self.assertEqual(res, False)

    def test_status_fails_when_status_missing(self):
        res = _smart.status_passed(INFO_DICT_STATUS_MISSING)
        self.assertEqual(res, False)

    def test_status_fails_when_status_block_missing(self):
        res = _smart.status_passed(INFO_DICT_STATUS_BLOCK_MISSING)
        self.assertEqual(res, False)

    def test_status_calls_smartctl(self):
        disable_logging()
        with patch("subprocess.run") as mock_run:
            _smart.device_info = MagicMock(return_value=INFO_DICT_STATUS_OK)
            _smart.status("/dev/dummy")
            mock_run.assert_called_with(
                ["smartctl", "--health", "--json", "/dev/dummy"], stdout=-1
            )

    def test_status_succeeds_when_drive_ok(self):
        disable_logging()
        with patch("subprocess.run") as _:
            _smart.device_info = MagicMock(return_value=INFO_DICT_STATUS_OK)
            res = _smart.status("/dev/dummy")
            self.assertEqual(
                res,
                DeviceTestResult(
                    device="/dev/dummy",
                    human_readable_name="SAMSUNG MZYLF128HCHP-000L2 - 119.2GB",
                    passed=True,
                    test_type=_smart_types.TestType.STATUS,
                    human_readable_error_info="",
                ),
            )
