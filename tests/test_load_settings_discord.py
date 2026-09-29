import json
import os
import tempfile
from unittest import TestCase

import _discord
import _load_settings
from _load_settings import Settings


class TestLoadSettings(TestCase):
    def test_missing_file_returns_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            settings = _load_settings._load_settings(os.path.join(d, "nope.json"))
        self.assertEqual(settings, Settings())

    def test_loads_valid_settings(self):
        content = {
            "CUSTOM_ALERT_LIMITS": {"/boot": 200000},
            "EXCLUDE_PATHS": ["/.snapshots", "/tmp"],
        }
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "settings.json")
            with open(path, "w") as f:
                json.dump(content, f)
            settings = _load_settings._load_settings(path)
        self.assertEqual(settings.custom_alert_limits, {"/boot": 200000})
        self.assertEqual(settings.exclude_paths, ("/.snapshots", "/tmp"))

    def test_explicit_path_overrides_default(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "settings.json")
            with open(path, "w") as f:
                json.dump(
                    {"CUSTOM_ALERT_LIMITS": {}, "EXCLUDE_PATHS": []}, f
                )
            settings = _load_settings._load_settings(settings_path=path)
        self.assertEqual(settings, Settings())


class TestDiscord(TestCase):
    def test_notify_discord_handles_missing_executable(self):
        # simulate notify-discord not on PATH -> FileNotFoundError -> logged, no crash
        from unittest.mock import patch

        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = _discord.notify_discord("hello")  # should not raise
        self.assertIsNone(result)

    def test_log_and_notify_discord_error_level(self):
        from unittest.mock import patch

        with patch("_discord.notify_discord") as mock_notify:
            _discord.log_and_notify_discord("boom", is_error=True)
        mock_notify.assert_called_once()
        args, kwargs = mock_notify.call_args
        self.assertEqual(args[0], "boom")
        self.assertTrue(args[1])