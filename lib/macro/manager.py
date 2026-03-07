from pathlib import Path
from typing import Dict, List, Optional

from .grammar import parse_macros
from .models import Macro


class MacroManager:
    """Manages the discovery, loading, and parsing of macro definitions."""

    def __init__(self, gamedir: Path) -> None:
        """Initialize the macro manager with the local game directory."""
        self.gamedir = gamedir
        self.global_dir = Path.home() / ".config" / "solo-rpg-cli"
        self.macros: Dict[str, Macro] = {}
        self.load_macros()

    def load_macros(self) -> None:
        """Clear and reload all global and local macros."""
        self.macros.clear()

        # load globals
        global_file = self.global_dir / "macros.txt"
        if global_file.exists():
            self._parse_file(global_file, is_global=True)

        # load locals
        local_file = self.gamedir / "macros.txt"
        if local_file.exists():
            self._parse_file(local_file, is_global=False)

    def _parse_file(self, filepath: Path, is_global: bool) -> None:
        """Parse a macros.txt file and append definitions to the cache."""
        with open(filepath, "r") as f:
            text = f.read()

        try:
            parsed_macros = parse_macros(text)
            for current_macro in parsed_macros:
                current_macro.is_global = is_global
                self.macros[current_macro.name] = current_macro
        except Exception as e:
            print(f"Error parsing macro file {filepath}: {e}")

    def get_macro(self, name: str) -> Optional[Macro]:
        """Fetch a macro by its designated name."""
        return self.macros.get(name)

    def list_macros(
        self, globals_only: bool = False, locals_only: bool = False
    ) -> List[Macro]:
        """Return a list of all currently loaded macros matching the scope criteria."""
        result = []
        for m in self.macros.values():
            if globals_only and not m.is_global:
                continue
            if locals_only and m.is_global:
                continue
            result.append(m)
        return result
