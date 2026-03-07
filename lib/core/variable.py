import json
from pathlib import Path
from typing import Any, Dict


class VariableManager:
    """Manages a collection of campaign variables persisted to a file."""

    def __init__(self, base_dir: Path):
        """Initialize the VariableManager with a base directory."""
        self.variables_file = base_dir / "variables.json"
        self._variables: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """Load variables from the JSON file into memory."""
        if self.variables_file.exists():
            try:
                with open(self.variables_file, "r") as f:
                    self._variables = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._variables = {}

    def _save(self):
        """Save variables from memory into the JSON file."""
        with open(self.variables_file, "w") as f:
            json.dump(self._variables, f, indent=4)

    def set_var(self, name: str, value: Any) -> None:
        """Add or update a variable and save it.

        Values are typically int, float, or str.
        """
        self._variables[name] = value
        self._save()

    def get_var(self, name: str, default: Any = None) -> Any:
        """Get the value of a variable, returning default if not found."""
        return self._variables.get(name, default)

    def delete_var(self, name: str) -> bool:
        """Delete a variable. Returns True if deleted, False if not found."""
        if name in self._variables:
            del self._variables[name]
            self._save()
            return True
        return False

    def get_all(self) -> Dict[str, Any]:
        """Get all variables as a dictionary."""
        return self._variables.copy()
