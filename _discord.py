# Requires the notify-discord executable on PATH
import subprocess


def notify_discord(message: str, is_error: bool = False):
    notify_args = ["notify-discord", message]
    if is_error:
        notify_args.extend(["--level", "error"])
    subprocess.run(notify_args)


def print_and_notify_discord(message: str, is_error: bool = False):
    print(message)
    notify_discord(message, is_error)
