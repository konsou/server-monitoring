from unittest import TestCase

from tests._test_data import SUCCESSFUL_SHORT_RESULT, FAILED_SHORT_RESULT


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
