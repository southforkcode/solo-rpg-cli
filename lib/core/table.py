import csv
import random
from pathlib import Path
from typing import List, Optional


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

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.tables_dir = self.base_dir / "tables"
        self.tables: dict[str, Table] = {}
        self.load_tables()

    def load_tables(self) -> None:
        """Scan the tables directory and load all table files."""
        self.tables.clear()
        if not self.tables_dir.exists() or not self.tables_dir.is_dir():
            return

        for p in self.tables_dir.iterdir():
            if p.is_file() and p.suffix in (".txt", ".csv"):
                table_name = p.stem
                self.tables[table_name] = Table(table_name, p)

    def roll(self, table_name: str) -> Optional[str]:
        """Roll on a specific table by name."""
        table = self.tables.get(table_name)
        if table:
            return table.roll()
        return None

    def list_tables(self) -> List[str]:
        """Return a sorted list of available table names."""
        return sorted(self.tables.keys())
