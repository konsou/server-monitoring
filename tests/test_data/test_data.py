import json
from pathlib import Path

import _smart_types

SCRIPT_DIR = script_dir = Path(__file__).resolve().parent

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

with open(SCRIPT_DIR / "info_dict_status_ok.json", encoding="utf-8") as f:
    INFO_DICT_STATUS_OK = json.load(f)
with open(SCRIPT_DIR / "info_dict_status_fail.json", encoding="utf-8") as f:
    INFO_DICT_STATUS_FAIL = json.load(f)
with open(SCRIPT_DIR / "info_dict_status_missing.json", encoding="utf-8") as f:
    INFO_DICT_STATUS_MISSING = json.load(f)
with open(SCRIPT_DIR / "info_dict_status_block_missing.json", encoding="utf-8") as f:
    INFO_DICT_STATUS_BLOCK_MISSING = json.load(f)
