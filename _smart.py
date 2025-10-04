import json
import subprocess


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
