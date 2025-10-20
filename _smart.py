import json
import logging
import subprocess
import time

import _smart_types

logger = logging.getLogger("server-monitoring")


def device_info(device: str) -> dict:
    i = subprocess.run(
        ["smartctl", "--xall", "--json", str(device)], stdout=subprocess.PIPE
    ).stdout.decode("utf-8")
    return json.loads(i)


def human_readable_error_info(device: str) -> str:
    i = subprocess.run(
        ["smartctl", "--log=selftest", "--log=error", "--log=xerror", str(device)],
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")
    return i


def human_readable_name(info_dict: dict) -> str:
    gb = 1024**3
    capacity_bytes = (
        info_dict.get("user_capacity", {}).get("bytes", None)
        or info_dict.get("nvme_total_capacity", None)
        or -1
    )
    return f"{info_dict.get('model_name', 'UNKNOWN')} - {capacity_bytes / gb:.1f}GB"


def device_from_info_dict(info_dict: dict) -> str:
    return info_dict.get("device", {}).get("name", "UNKNOWN")


def poll_time(info_dict: dict) -> int:
    try:
        return int(
            info_dict["ata_smart_data"]["self_test"]["polling_minutes"]["short"] * 60
        )
    except KeyError:
        # Polling time not available - default
        return 60


def test_in_progress(info_dict: dict) -> bool:
    if "ata_smart_data" in info_dict:
        val = (
            info_dict.get("ata_smart_data", {})
            .get("self_test", {})
            .get("status", {})
            .get("string", "")
        )
        return "in progress" in val
    return bool(
        info_dict.get("nvme_self_test_log", {})
        .get("current_self_test_operation", {})
        .get("value", 0)
    )


def test_passed(info_dict: dict) -> bool:
    if "ata_smart_data" in info_dict:
        return (
            info_dict.get("ata_smart_data", {})
            .get("self_test", {})
            .get("status", {})
            .get("passed", False)
        )

    try:
        result = (
            info_dict.get("nvme_self_test_log", {})
            .get("table", [])[0]
            .get("self_test_result", {})
            .get("value", 1)
        )
        # result value 0 = passed - flip to get success boolean
        return not result
    # nvme self test log doesn't exist
    except IndexError:
        return False


def status_passed(info_dict: dict) -> bool:
    return info_dict.get("smart_status", {}).get("passed", False)


def scan_devices() -> list[str]:
    entries = subprocess.run(
        ["smartctl", "--scan", "--json"], stdout=subprocess.PIPE
    ).stdout.decode("utf-8")
    parsed = json.loads(entries)
    return [d["info_name"] for d in parsed["devices"]]


def status(device: str) -> _smart_types.DeviceTestResult:
    _device_info = device_info(device)
    _human_readable_name = human_readable_name(_device_info)
    logger.info(f"Getting SMART status for {device} - {_human_readable_name}...")
    subprocess.run(
        ["smartctl", "--health", "--json", str(device)], stdout=subprocess.PIPE
    ).stdout.decode("utf-8")

    # Update device info in case the smartctl command updated state
    _device_info = device_info(device)

    _log_test_result(_device_info)

    passed = status_passed(_device_info)
    error_info = "" if passed else human_readable_error_info(device)
    return _smart_types.DeviceTestResult(
        device=device,
        human_readable_name=_human_readable_name,
        passed=passed,
        test_type=_smart_types.TestType.STATUS,
        human_readable_error_info=error_info,
    )


def status_all() -> _smart_types.TestResults:
    tests_passed = True
    devices = scan_devices()
    device_results = []
    for device in devices:
        result = status(device)
        device_results.append(result)
        tests_passed = tests_passed and result.passed
    return _smart_types.TestResults(passed=tests_passed, results=tuple(device_results))


def short(device: str) -> _smart_types.DeviceTestResult:
    _device_info = device_info(device)
    _poll_time = poll_time(_device_info)
    _human_readable_name = human_readable_name(_device_info)
    logger.info(f"Starting short self-test for {device} - {_human_readable_name}...")
    subprocess.run(["smartctl", "--test=short", "--json", str(device)])
    logger.info(f"Polling results every {_poll_time / 60} minutes")
    while True:
        time.sleep(_poll_time)
        _device_info = device_info(device)
        if not test_in_progress(_device_info):
            break
        logger.info(
            f"Test still in progress. Waiting another {_poll_time / 60} minutes",
        )

    _log_test_result(_device_info)

    passed = test_passed(_device_info)
    error_info = "" if passed else human_readable_error_info(device)
    return _smart_types.DeviceTestResult(
        device=device,
        human_readable_name=_human_readable_name,
        passed=passed,
        test_type=_smart_types.TestType.SHORT,
        human_readable_error_info=error_info,
    )


def _log_test_result(info_dict: dict):
    passed = test_passed(info_dict)
    _human_readable_name = human_readable_name(info_dict)
    device = device_from_info_dict(info_dict)
    if passed:
        logger.info(f"passed: {device} - {_human_readable_name}")
    else:
        logger.error(f"FAILED: {device} - {_human_readable_name}")


def short_all() -> _smart_types.TestResults:
    tests_passed = True
    devices = scan_devices()
    device_results = []
    for device in devices:
        result = short(device)
        device_results.append(result)
        tests_passed = tests_passed and result.passed
    return _smart_types.TestResults(passed=tests_passed, results=tuple(device_results))
