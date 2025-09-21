#!/usr/bin/env python3
import subprocess
import sys
from typing import NamedTuple, Tuple, List

GB = 1024 * 1024
DEFAULT_ALERT_LIMIT = 50 * GB
# TODO: load these from a conf file
CUSTOM_ALERT_LIMITS = {
    "/boot": 200_000,
    "/mnt/seagate-12t": 500 * GB,
}
EXCLUDE_DEVICES = ("/.snapshots",)


class DeviceEntry(NamedTuple):
    # Mount point or zpool name
    name: str
    free_space: int


def notify_discord(message: str, is_error: bool = False):
    notify_args = ["notify-discord", message]
    if is_error:
        notify_args.extend(["--level", "error"])
    subprocess.run(notify_args)


def print_and_notify_discord(message: str, is_error: bool = False):
    print(message)
    notify_discord(message, is_error)


def _parse_and_filter_entries(entries: List[str]) -> Tuple[DeviceEntry, ...]:
    tmp_entries = []
    for e in entries:
        name, free_space = e.strip().split()
        name = name.strip()
        free_space = int(free_space.strip())
        if name in EXCLUDE_DEVICES:
            continue
        tmp_entries.append(DeviceEntry(name, free_space))
    return tuple(tmp_entries)


def zpool_free_space() -> Tuple[DeviceEntry, ...]:
    try:
        entries = (
            subprocess.run(
                ["zpool", "list", "-Hp", "-o", "name,free"], stdout=subprocess.PIPE
            )
            .stdout.decode("utf-8")
            .splitlines()
        )
    except FileNotFoundError:
        # zfs not installed, zpool command not available
        return ()
    return _parse_and_filter_entries(entries)


def devices_free_space() -> Tuple[DeviceEntry, ...]:
    entries = (
        subprocess.run(
            [
                "df",
                "--output=target,avail",
                "--exclude-type=overlay",
                "--exclude-type=tmpfs",
                "--exclude-type=zfs",
            ],
            stdout=subprocess.PIPE,
        )
        .stdout.decode("utf-8")
        .splitlines()[1:]  # First line is captions
    )

    df_results = _parse_and_filter_entries(entries)
    zpool_results = zpool_free_space()
    return df_results + zpool_results


has_alerts = False
messages = []
low_space_devices = []

free_space_entries = devices_free_space()
for entry in free_space_entries:
    if not entry:
        continue

    alert_limit = CUSTOM_ALERT_LIMITS.get(entry.name, DEFAULT_ALERT_LIMIT)
    if entry.free_space < alert_limit:
        start_of_line = f"LOW SPACE:"
        has_alerts = True
        low_space_devices.append(entry.name)
    else:
        start_of_line = f"ok:"

    info_text = f"{start_of_line} {entry.name}: {entry.free_space / GB:.2f} GB ({alert_limit / GB:.2f} GB)"
    messages.append(info_text)

if has_alerts:
    messages.insert(0, f"ALERT - LOW DISK SPACE ON {', '.join(low_space_devices)}")
else:
    messages.insert(0, "Disk space OK")

print_and_notify_discord("\n".join(messages), has_alerts)
sys.exit(has_alerts)
