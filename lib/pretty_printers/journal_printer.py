from datetime import datetime
from typing import Any, List

from lib.journal import JournalEntry
from lib.pretty import PrettyPrinter


class JournalPrinter(PrettyPrinter):
    def can_print(self, obj: Any) -> bool:
        return isinstance(obj, list) and all(isinstance(x, JournalEntry) for x in obj)

    def print(self, obj: List[JournalEntry]) -> None:
        if not obj:
            print("No journal entries found.")
            return

        for i, entry in enumerate(obj, start=1):
            dt = datetime.fromtimestamp(entry.timestamp)
            print(f"[{i}] {entry.title} - {dt.strftime('%c')}")
            print(entry.content)
            print("-" * 40)
