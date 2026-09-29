from unittest import TestCase

from _load_settings import Settings
from tests.conftest import check_free_space


class TestConstants(TestCase):
    def test_gb_is_one_gibibyte(self):
        # Regression: GB was previously 1024*1024 (1 MiB), inflating free-space
        # figures by 1024x and shrinking the alert limit by 1024x.
        self.assertEqual(check_free_space.GB, 1024**3)

    def test_default_alert_limit_is_50_gib(self):
        self.assertEqual(check_free_space.DEFAULT_ALERT_LIMIT, 50 * 1024**3)


class TestParseEntries(TestCase):
    def test_parses_normal_entry(self):
        entries = check_free_space._parse_and_filter_entries(
            ["/ 1000"], Settings()
        )
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].name, "/")
        self.assertEqual(entries[0].free_space, 1000)
        self.assertFalse(entries[0].ignored)

    def test_excluded_path_is_flagged_ignored(self):
        settings = Settings(exclude_paths=("/.snapshots",))
        entries = check_free_space._parse_and_filter_entries(
            ["/.snapshots -1"], settings
        )
        self.assertTrue(entries[0].ignored)
        self.assertEqual(entries[0].free_space, check_free_space.IGNORED)

    def test_invalid_line_raises(self):
        with self.assertRaises(ValueError):
            check_free_space._parse_and_filter_entries(["garbage"], Settings())


class TestEvaluate(TestCase):
    def _entry(self, name, free):
        return check_free_space.DeviceEntry(name=name, free_space=free)

    def test_ok_when_above_limit(self):
        report = check_free_space.evaluate_free_space(
            (self._entry("/", 200 * check_free_space.GB),), Settings()
        )
        self.assertFalse(report.has_alerts)
        self.assertEqual(report.overall_status, "Disk space OK")
        self.assertEqual(report.low_space_devices, ())

    def test_alert_when_below_default_limit(self):
        report = check_free_space.evaluate_free_space(
            (self._entry("/", 10 * check_free_space.GB),),
            Settings(),
            default_alert_limit=50 * check_free_space.GB,
        )
        # 10 GiB < 50 GiB default -> alert
        self.assertEqual(report.low_space_devices, ("/",))
        self.assertTrue(report.has_alerts)
        self.assertTrue(report.overall_status.startswith("ALERT"))

    def test_custom_limit_lowers_threshold(self):
        settings = Settings(custom_alert_limits={"/": 2 * check_free_space.GB})
        report = check_free_space.evaluate_free_space(
            (self._entry("/", 5 * check_free_space.GB),), settings
        )
        # 5 GiB > 2 GiB custom limit -> OK despite 50 GiB default
        self.assertFalse(report.has_alerts)

    def test_ignored_entry_never_alerts(self):
        entry = check_free_space.DeviceEntry(
            name="/.snapshots", free_space=check_free_space.IGNORED, ignored=True
        )
        report = check_free_space.evaluate_free_space((entry,), Settings())
        self.assertFalse(report.has_alerts)
        first_row = report.rows[1]
        self.assertEqual(first_row[0], "ignored")

    def test_multiple_alert_devices_combined(self):
        report = check_free_space.evaluate_free_space(
            (
                self._entry("/", 1 * check_free_space.GB),
                self._entry("/data", 2 * check_free_space.GB),
                self._entry("/home", 200 * check_free_space.GB),
            ),
            Settings(),
        )
        self.assertEqual(set(report.low_space_devices), {"/", "/data"})
        self.assertIn("/", report.overall_status)
        self.assertIn("/data", report.overall_status)
        self.assertNotIn("/home", report.overall_status)


class TestFormat(TestCase):
    def test_format_produces_table(self):
        report = check_free_space.evaluate_free_space(
            (check_free_space.DeviceEntry(name="/", free_space=100 * check_free_space.GB),),
            Settings(),
        )
        out = check_free_space.format_report(report)
        self.assertIn("Status", out)
        self.assertIn("/", out)