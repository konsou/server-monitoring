from unittest import TestCase

import _smart

from tests.test_data import (
    SUCCESSFUL_SHORT_RESULT,
    FAILED_SHORT_RESULT,
    INFO_DICT_STATUS_OK,
    INFO_DICT_STATUS_FAIL,
    INFO_DICT_STATUS_MISSING,
    INFO_DICT_STATUS_BLOCK_MISSING,
)


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
