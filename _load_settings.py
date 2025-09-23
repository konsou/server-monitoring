import json
import os
from typing import NamedTuple


class Settings(NamedTuple):
    custom_alert_limits: dict[str, int] = {}
    exclude_paths: tuple[str, ...] = ()


def _load_settings() -> Settings:
    script_dir = os.path.dirname(os.path.realpath(__file__))
    settings_full_path = os.path.join(script_dir, "settings.json")

    if not os.path.isfile(settings_full_path):
        print(f"{settings_full_path} not found, using defaults")
        return Settings()

    with open(settings_full_path, encoding="utf-8") as settings_file:
        settings_json = json.load(settings_file)

    return Settings(
        custom_alert_limits=settings_json["CUSTOM_ALERT_LIMITS"],
        exclude_paths=tuple(settings_json["EXCLUDE_PATHS"]),
    )
