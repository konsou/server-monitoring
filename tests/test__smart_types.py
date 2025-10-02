from unittest import TestCase

import _smart_types

SUCCESSFUL_SHORT_RESULT = _smart_types.DeviceTestResult(
    device="/dev/sda",
    human_readable_name="SAMSUNG MZYLF128HCHP-000L2 - 119.2GB",
    passed=True,
    test_type=_smart_types.TestType.SHORT,
    human_readable_error_info="",
)
FAILED_SHORT_RESULT = _smart_types.DeviceTestResult(
    device="/dev/sda",
    human_readable_name="UNKNOWN - 0.4GB",
    passed=False,
    test_type=_smart_types.TestType.SHORT,
    human_readable_error_info="smartctl 7.4 2023-08-01 r5530 [x86_64-linux-6.6.87.2-microsoft-standard-WSL2] (local build)\nCopyright (C) 2002-23, Bruce Allen, Christian Franke, www.smartmontools.org\n\n=== START OF READ SMART DATA SECTION ===\nError Counter logging not supported\n\nDevice does not support Self Test logging\n",
)


class TestDeviceTestResult(TestCase):
    def test_as_table_row_successful(self):
        result = SUCCESSFUL_SHORT_RESULT.as_table_row()
        self.assertEqual(
            result,
            (
                "ok",
                SUCCESSFUL_SHORT_RESULT.device,
                SUCCESSFUL_SHORT_RESULT.human_readable_name,
            ),
        )

    def test_as_table_row_failed(self):
        result = FAILED_SHORT_RESULT.as_table_row()
        self.assertEqual(
            result,
            (
                "FAILED",
                FAILED_SHORT_RESULT.device,
                FAILED_SHORT_RESULT.human_readable_name,
            ),
        )
