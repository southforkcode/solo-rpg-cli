import logging
import tomllib
from pathlib import Path
from typing import Any, Dict, TypeVar, Union, overload

T = TypeVar("T")
TomlType = Union[Dict[str, "TomlType"], list["TomlType"], str, int, float, bool, None]

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manages the discovery and parsing of TOML settings files."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.settings_dir = self.base_dir / "settings"
        self.settings: Dict[str, TomlType] = {}
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
                                current_dict: Dict[str, Any] = self.settings[k]  # type: ignore
                                current_dict.update(v)
                            else:
                                self.settings[k] = v
                except tomllib.TOMLDecodeError as e:
                    logger.error(f"Error decoding TOML file {p.name}: {e}")

    @overload
    def get(self, key: str) -> TomlType: ...

    @overload
    def get(self, key: str, default: T) -> T | TomlType: ...

    def get(self, key: str, default: TomlType | T = None) -> TomlType | T:
        return self.settings.get(key, default)
