import tomllib
from pathlib import Path
from typing import Any


class SettingsManager:
    """Manages the discovery and parsing of TOML settings files."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.settings_dir = self.base_dir / "settings"
        self.settings: dict[str, Any] = {}
        self.load_settings()

    def load_settings(self) -> None:
        """Scan the settings directory and load all .toml files into a single dict."""
        self.settings.clear()
        if not self.settings_dir.exists() or not self.settings_dir.is_dir():
            return

        for p in self.settings_dir.glob("*.toml"):
            if p.is_file():
                try:
                    with open(p, "rb") as f:
                        data = tomllib.load(f)
                        # Merge dictionaries at the top level to allow different files
                        # to contribute to sections like [tables]
                        for k, v in data.items():
                            if (
                                k in self.settings
                                and isinstance(self.settings[k], dict)
                                and isinstance(v, dict)
                            ):
                                self.settings[k].update(v)
                            else:
                                self.settings[k] = v
                except tomllib.TOMLDecodeError as e:
                    print(f"Error decoding TOML file {p.name}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)
