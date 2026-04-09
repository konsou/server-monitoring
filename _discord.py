# Requires the notify-discord executable on PATH
import logging
import subprocess

logger = logging.getLogger("server-monitoring")


def notify_discord(message: str, is_error: bool = False):
    notify_args = ["notify-discord", message]
    if is_error:
        notify_args.extend(["--level", "error"])

    try:
        notify_result = subprocess.run(notify_args, capture_output=True, text=True)
    except FileNotFoundError:
        logger.error(
            f"notify-discord executable not found in path, can't send discord notifications"
        )
        return

    if notify_result.returncode == 0:
        logger.info(notify_result.stdout)
    else:
        logger.error(f"Could not send Discord message: {notify_result.stdout}")


def log_and_notify_discord(message: str, is_error: bool = False):
    if is_error:
        logger.error(message)
    else:
        logger.info(message)
    notify_discord(message, is_error)
