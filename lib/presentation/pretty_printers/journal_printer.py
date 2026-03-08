from datetime import datetime

from rich.console import Console

from lib.core.journal import JournalEntry
from lib.presentation.pretty import PrettyPrinter


class JournalPrinter(PrettyPrinter):
    def can_print(self, obj: object) -> bool:
        return isinstance(obj, list) and all(isinstance(x, JournalEntry) for x in obj)

    def print(self, obj: object) -> None:
        assert isinstance(obj, list)
        console = Console()
        if not obj:
            console.print("No journal entries found.")
            return

        for i, entry in enumerate(obj, start=1):
            dt = datetime.fromtimestamp(entry.timestamp)
            console.print(
                f"[italic gray][{i}] {entry.title} - {dt.strftime('%c')}[/italic gray]"
            )
            console.print(f"[italic gray]{entry.content}[/italic gray]")
            console.print(f"[italic gray]{'-' * 40}[/italic gray]")
