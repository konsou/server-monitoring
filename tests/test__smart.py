import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch, call

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

    @patch("_smart.device_info")
    @patch("subprocess.run")
    def test_status_calls_smartctl(self, mock_run, mock_device_info):
        disable_logging()
        mock_device_info.return_value = INFO_DICT_STATUS_OK
        _smart.status("/dev/dummy")
        mock_run.assert_called_with(
            ["smartctl", "--health", "--json", "/dev/dummy"], stdout=-1
        )

    @patch("_smart.human_readable_error_info")
    @patch("_smart.device_info")
    @patch("subprocess.run")
    def test_status_succeeds_when_drive_ok(
        self, _, mock_device_info, mock_human_readable_error_info
    ):
        disable_logging()
        mock_device_info.return_value = INFO_DICT_STATUS_OK
        mock_human_readable_error_info.return_value = ""
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

    @patch("_smart.human_readable_error_info")
    @patch("_smart.device_info")
    @patch("subprocess.run")
    def test_status_fails_when_drive_not_ok(
        self, _, mock_device_info, mock_human_readable_error_info
    ):
        disable_logging()
        mock_device_info.return_value = INFO_DICT_STATUS_FAIL
        mock_human_readable_error_info.return_value = "Mock error info"
        res = _smart.status("/dev/dummy")
        self.assertEqual(
            res,
            DeviceTestResult(
                device="/dev/dummy",
                human_readable_name="SAMSUNG MZYLF128HCHP-000L2 - 119.2GB",
                passed=False,
                test_type=_smart_types.TestType.STATUS,
                human_readable_error_info="Mock error info",
            ),
        )

    @patch("_smart.status")
    @patch("_smart.scan_devices")
    def test_status_all_calls_status(self, mock_scan, mock_status):
        disable_logging()
        mock_scan.return_value = ("/dev/sda", "/dev/sdb", "/dev/sdc")

        _smart.status_all()
        self.assertEqual(
            len(mock_status.call_args_list),
            3,
            msg="status() should be called for every device",
        )
        self.assertEqual(
            mock_status.call_args_list,
            [call("/dev/sda"), call("/dev/sdb"), call("/dev/sdc")],
            msg="status() should be called with correct device names",
        )

    @patch("_smart.poll_time")
    @patch("_smart.device_info")
    @patch("subprocess.run")
    def test_short_calls_smartctl(self, mock_run, mock_device_info, mock_poll_time):
        disable_logging()
        mock_device_info.return_value = INFO_DICT_STATUS_OK
        mock_poll_time.return_value = 0
        _smart.short("/dev/dummy")
        mock_run.assert_called_with(
            ["smartctl", "--test=short", "--json", "/dev/dummy"]
        )

    @patch("_smart.poll_time")
    @patch("_smart.human_readable_error_info")
    @patch("_smart.device_info")
    @patch("subprocess.run")
    def test_short_succeeds_when_drive_ok(
        self, _, mock_device_info, mock_human_readable_error_info, mock_poll_time
    ):
        disable_logging()
        mock_device_info.return_value = INFO_DICT_STATUS_OK
        mock_human_readable_error_info.return_value = ""
        mock_poll_time.return_value = 0
        res = _smart.short("/dev/dummy")
        self.assertEqual(
            res,
            DeviceTestResult(
                device="/dev/dummy",
                human_readable_name="SAMSUNG MZYLF128HCHP-000L2 - 119.2GB",
                passed=True,
                test_type=_smart_types.TestType.SHORT,
                human_readable_error_info="",
            ),
        )

    @patch("_smart.test_passed")
    @patch("_smart.poll_time")
    @patch("_smart.human_readable_error_info")
    @patch("_smart.device_info")
    @patch("subprocess.run")
    def test_short_fails_when_drive_not_ok(
        self,
        _,
        mock_device_info,
        mock_human_readable_error_info,
        mock_poll_time,
        mock_test_passed,
    ):
        disable_logging()
        mock_device_info.return_value = INFO_DICT_STATUS_FAIL
        mock_human_readable_error_info.return_value = "Mock error info"
        mock_poll_time.return_value = 0
        mock_test_passed.return_value = False
        res = _smart.short("/dev/dummy")
        self.assertEqual(
            DeviceTestResult(
                device="/dev/dummy",
                human_readable_name="SAMSUNG MZYLF128HCHP-000L2 - 119.2GB",
                passed=False,
                test_type=_smart_types.TestType.SHORT,
                human_readable_error_info="Mock error info",
            ),
            res,
        )

    @patch("_smart.short")
    @patch("_smart.scan_devices")
    def test_short_all_calls_short(self, mock_scan, mock_short):
        disable_logging()
        mock_scan.return_value = ("/dev/sda", "/dev/sdb", "/dev/sdc")

        _smart.short_all()
        self.assertEqual(
            len(mock_short.call_args_list),
            3,
            msg="short() should be called for every device",
        )
        self.assertEqual(
            mock_short.call_args_list,
            [call("/dev/sda"), call("/dev/sdb"), call("/dev/sdc")],
            msg="short() should be called with correct device names",
        )
