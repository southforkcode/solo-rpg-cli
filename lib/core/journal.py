from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class JournalEntry:
    """A single journal entry containing a title, content, and a timestamp."""

    title: str
    content: str
    timestamp: float

    def to_dict(self) -> dict:
        """Convert the entry to a dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "JournalEntry":
        """Create a JournalEntry from a dictionary representing its fields."""
        return cls(
            title=data["title"],
            content=data["content"],
            timestamp=data["timestamp"],
        )


class JournalManager:
    """Manages a collection of journal entries persisted to a file."""

    def __init__(self, base_dir: Path):
        """Initialize the JournalManager with a base directory."""
        self.journal_file = base_dir / "journal.txt"
        self._entries: List[JournalEntry] = []
        self._load()

    def _load(self):
        """Load entries from the journal file into memory."""
        if self.journal_file.exists():
            with open(self.journal_file, "r") as f:
                content = f.read()
                entries_data = content.split("\n\n---\n\n")
                for entry_data in entries_data:
                    if not entry_data.strip():
                        continue
                    lines = entry_data.strip().split("\n")
                    if len(lines) >= 2:
                        title = lines[0]
                        timestamp_str = lines[1]
                        try:
                            timestamp = float(timestamp_str)
                        except ValueError:
                            timestamp = 0.0
                        content = "\n".join(lines[2:])
                        self._entries.append(
                            JournalEntry(
                                title=title, content=content, timestamp=timestamp
                            )
                        )

    def _save(self):
        """Save entries from memory into the journal file."""
        with open(self.journal_file, "w") as f:
            for i, entry in enumerate(self._entries):
                f.write(f"{entry.title}\n{entry.timestamp}\n{entry.content}")
                if i < len(self._entries) - 1:
                    f.write("\n\n---\n\n")

    def add_entry(self, entry: JournalEntry):
        """Add a new entry to the journal and save it."""
        self._entries.append(entry)
        self._save()

    def get_entries(self, top: Optional[int] = None) -> List[JournalEntry]:
        """Get a list of journal entries, limited to top N if specified."""
        if top is None:
            return self._entries.copy()
        return self._entries[-top:]

    def delete_entry(self, identifier: str) -> bool:
        """Delete a journal entry by its 1-based index or its exact title."""
        # Check if identifier is an index (1-based)
        try:
            index = int(identifier)
            if 1 <= index <= len(self._entries):
                del self._entries[index - 1]
                self._save()
                return True
        except ValueError:
            pass

        # Fallback to delete by title
        for i, entry in enumerate(self._entries):
            if entry.title == identifier:
                del self._entries[i]
                self._save()
                return True

        return False
