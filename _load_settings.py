import json
import os
from typing import NamedTuple


class Settings(NamedTuple):
    custom_alert_limits: dict[str, int] = {}
    exclude_paths: tuple[str, ...] = ()


def _load_settings(settings_path: str | None = None) -> Settings:
    """Load settings from settings.json next to this module.

    If `settings_path` is given (e.g. from a test), use it directly instead.
    Returns defaults when no settings file exists.
    """
    if settings_path is None:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        settings_path = os.path.join(script_dir, "settings.json")

    if not os.path.isfile(settings_path):
        print(f"{settings_path} not found, using defaults")
        return Settings()

    with open(settings_path, encoding="utf-8") as settings_file:
        settings_json = json.load(settings_file)

    return Settings(
        custom_alert_limits=settings_json["CUSTOM_ALERT_LIMITS"],
        exclude_paths=tuple(settings_json["EXCLUDE_PATHS"]),
    )