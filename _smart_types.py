import enum
from typing import NamedTuple

import tabulate


class TestType(enum.Enum):
    STATUS = enum.auto()
    SHORT = enum.auto()
    LONG = enum.auto()


class DeviceTestResult(NamedTuple):
    device: str
    human_readable_name: str
    passed: bool
    test_type: TestType
    human_readable_error_info: str = ""

    def as_table_row(self) -> tuple[str, str, str]:
        return (
            "ok" if self.passed else "FAILED",
            self.device,
            self.human_readable_name,
        )


class TestResults(NamedTuple):
    passed: bool
    results: tuple[DeviceTestResult, ...]

    def as_table(self) -> str:
        return tabulate.tabulate(self.results, headers=("Status", "Device", "Info"))
