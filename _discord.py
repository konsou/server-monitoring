# Requires the notify-discord executable on PATH
import logging
import subprocess

logger = logging.getLogger("server-monitoring")


def notify_discord(message: str, is_error: bool = False):
    notify_args = ["notify-discord", message]
    if is_error:
        notify_args.extend(["--level", "error"])
    subprocess.run(notify_args)


def log_and_notify_discord(message: str, is_error: bool = False):
    if is_error:
        logger.error(message)
    else:
        logger.info(message)
    notify_discord(message, is_error)
