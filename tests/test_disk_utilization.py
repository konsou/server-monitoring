from unittest import TestCase

from tests.conftest import disk_utilization, disk_utilization_gatherer


class TestParseLog(TestCase):
    def test_parses_valid_lines(self):
        stats = disk_utilization.parse_log("100.0,sda,5\n200.0,sda,7\n150.0,nvme0n1,3\n")
        self.assertEqual(set(stats.keys()), {"sda", "nvme0n1"})
        self.assertEqual(stats["sda"].util_values, [5, 7])
        self.assertEqual(stats["sda"].timestamps, [100.0, 200.0])

    def test_skips_malformed_lines(self):
        stats = disk_utilization.parse_log("garbage\n100,sda\nsda,5,9,1\n100,,\n")
        self.assertEqual(stats, {})

    def test_skips_blank_name(self):
        stats = disk_utilization.parse_log("100,,5\n")
        self.assertEqual(stats, {})


class TestDeviceStats(TestCase):
    def _stats(self, values):
        s = disk_utilization.DeviceStats(name="sda")
        s.util_values = values
        s.timestamps = list(range(len(values)))
        return s

    def test_max_min_avg_median(self):
        s = self._stats([10, 20, 30, 40])
        self.assertEqual(s.max_util(), 40)
        self.assertEqual(s.min_util(), 10)
        self.assertEqual(s.avg_util(), 25)
        self.assertEqual(s.median_util(), 25)

    def test_max_util_and_timestamp(self):
        s = self._stats([5, 50, 20])
        value, ts = s.max_util_and_timestamp()
        self.assertEqual(value, 50)
        self.assertEqual(ts, 1)

    def test_warning_thresholds(self):
        self.assertTrue(self._stats([99]).status_warning())
        self.assertTrue(self._stats([60, 60]).status_warning())
        self.assertTrue(self._stats([51, 49]).status_warning())
        self.assertFalse(self._stats([10, 20, 30]).status_warning())

    def test_critical_thresholds(self):
        self.assertTrue(self._stats([95, 96]).status_critical())
        self.assertFalse(self._stats([50, 60]).status_critical())


class TestIsActualDisk(TestCase):
    def test_physical_disks(self):
        self.assertTrue(disk_utilization.is_actual_disk("sda"))
        self.assertTrue(disk_utilization.is_actual_disk("nvme0n1"))

    def test_non_physical_disks(self):
        self.assertFalse(disk_utilization.is_actual_disk("loop0"))
        self.assertFalse(disk_utilization.is_actual_disk("dm-0"))
        self.assertFalse(disk_utilization.is_actual_disk("sr0"))


class TestGathererSampling(TestCase):
    IOSTAT_JSON = """
    {"sysstat": {"hosts": [{"statistics": [{"disk": [
        {"disk_device": "loop0", "util": 1},
        {"disk_device": "sda", "util": 42.5},
        {"disk_device": "nvme0n1", "util": 7}
    ]}]}]}}
    """

    def test_returns_first_physical_disk(self):
        row = disk_utilization_gatherer.sample_disk_utilization(123.0, self.IOSTAT_JSON)
        self.assertEqual(row, "123.0,sda,42.5")

    def test_returns_none_when_no_physical_disk(self):
        j = '{"sysstat": {"hosts": [{"statistics": [{"disk": [{"disk_device": "loop0", "util": 1}]}]}]}}'
        result = disk_utilization_gatherer.sample_disk_utilization(123.0, j)
        self.assertIsNone(result)

    def test_gatherer_is_actual_disk(self):
        self.assertTrue(disk_utilization_gatherer.is_actual_disk("sdb"))
        self.assertFalse(disk_utilization_gatherer.is_actual_disk("loop1"))