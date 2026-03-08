import csv
import logging
import random
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from lib.core.settings import SettingsManager


class Table:
    """Represents a random roll table loaded from a file."""

    def __init__(self, name: str, filepath: Path):
        self.name = name
        self.filepath = filepath
        self.items: List[str] = []
        self._load()

    def _load(self) -> None:
        """Load the items from the file based on the extension."""
        if not self.filepath.exists():
            return

        with open(self.filepath, "r", encoding="utf-8") as f:
            if self.filepath.suffix == ".csv":
                reader = csv.reader(f)
                for row in reader:
                    # use the first column if available
                    if row:
                        self.items.append(row[0].strip())
            else:
                for line in f:
                    line = line.strip()
                    if line:
                        self.items.append(line)

    def roll(self) -> Optional[str]:
        """Roll on the table and return a random item."""
        if not self.items:
            return None
        return random.choice(self.items)


class TableManager:
    """Manages the discovery, loading, and rolling of random tables."""

    def __init__(
        self, base_dir: Path, settings_manager: Optional["SettingsManager"] = None
    ):
        self.base_dir = base_dir
        self.settings_manager = settings_manager
        self.tables_dir = self.base_dir / "tables"
        self.tables: dict[str, Table] = {}
        self.load_tables()

    def load_tables(self) -> None:
        """Scan the tables directory and load all table files."""
        self.tables.clear()

        # 1. Load default tables
        if self.tables_dir.exists() and self.tables_dir.is_dir():
            for p in self.tables_dir.iterdir():
                if p.is_file() and p.suffix in (".txt", ".csv"):
                    table_name = p.stem
                    self.tables[table_name] = Table(table_name, p)

        # 2. Load table includes from settings
        if self.settings_manager:
            tables_config = self.settings_manager.get("tables", {})
            if isinstance(tables_config, dict):
                dict_config: dict[str, Any] = tables_config  # type: ignore
                for name, path_str in dict_config.items():
                    if not isinstance(path_str, str):
                        continue
                    p = (self.settings_manager.settings_dir / path_str).resolve()
                    if "*" in p.name:
                        # Glob support
                        parent_dir = p.parent
                        if not parent_dir.exists() or not parent_dir.is_dir():
                            logger.warning(
                                f"Table include directory not found: {parent_dir}"
                            )
                            continue

                        found = False
                        for match in parent_dir.glob(p.name):
                            if match.is_file() and match.suffix in (".txt", ".csv"):
                                table_name = match.stem
                                self.tables[table_name] = Table(table_name, match)
                                found = True
                        if not found:
                            logger.warning(f"No tables found matching glob: {p}")
                    else:
                        if not p.exists() or not p.is_file():
                            logger.warning(f"Table include file not found: {p}")
                        else:
                            self.tables[name] = Table(name, p)

    def roll(self, table_name: str) -> Optional[str]:
        """Roll on a specific table by name."""
        table = self.tables.get(table_name)
        if table:
            return table.roll()
        return None

    def list_tables(self) -> List[str]:
        """Return a sorted list of available table names."""
        return sorted(self.tables.keys())
