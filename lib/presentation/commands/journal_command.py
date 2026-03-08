from datetime import datetime
from typing import Any

import prompt_toolkit
from rich.console import Console

from lib.core.journal import JournalEntry
from lib.core.state import State
from lib.presentation.command import Command
from lib.presentation.lexer import Lexer


def prompt(*args, **kwargs):
    return prompt_toolkit.prompt(*args, **kwargs)


class JournalCommand(Command):
    """The command for managing journal entries through adding, listing, or deleting."""

    def __init__(self):
        """Initialize the JournalCommand."""
        super().__init__()
        self.command = "journal"
        self.aliases = ["j"]
        self.description = "Manage journal entries"

    def get_completions(self, text_before_cursor: str, state: State) -> list[str]:
        """Return a list of autocomplete suggestions."""
        words = text_before_cursor.split()
        if not words:
            return []

        is_new_word = text_before_cursor.endswith(" ")
        verbs = ["add", "list", "delete", "del"]

        if len(words) == 1 and not is_new_word:
            return []

        if len(words) == 1 and is_new_word:
            return verbs

        if len(words) == 2 and not is_new_word:
            prefix = words[1].lower()
            return [v for v in verbs if v.startswith(prefix)]

        return []

    def execute(self, lexer: Lexer, state: State) -> object:
        """Execute the journal command by routing to the appropriate subcommand."""
        subcommand = lexer.next()

        if not subcommand:
            return self.help()

        if subcommand == "add":
            return self.add_subcommand(lexer, state)
        elif subcommand == "list":
            return self.list_subcommand(lexer, state)
        elif subcommand in ["delete", "del"]:
            return self.delete_subcommand(lexer, state)
        else:
            return f"Error: Unknown journal subcommand '{subcommand}'"

    def add_subcommand(self, lexer: Lexer, state: State) -> Any:
        """Handle the 'add' subcommand to write a new journal entry."""
        title_parts = []
        while True:
            part = lexer.next()
            if part is None:
                break
            title_parts.append(part)

        if title_parts:
            title = " ".join(title_parts)
        else:
            title = f"Note at {datetime.now().strftime('%c')}"

        print(
            "Adding journal entry... (Type '...' on a new line or "
            "press Ctrl-D to save, Ctrl-C to cancel)"
        )
        content_lines = []
        try:
            while True:
                line = prompt("j>")
                if line.strip() == "...":
                    break
                content_lines.append(line)
        except EOFError:
            pass  # Ctrl-D
        except KeyboardInterrupt:
            return "Note cancelled."

        content = "\n".join(content_lines)
        entry = JournalEntry(
            title=title, content=content, timestamp=datetime.now().timestamp()
        )
        state.journal_manager.add_entry(entry)
        return "Journal entry added."

    def list_subcommand(self, lexer: Lexer, state: State) -> Any:
        """Handle the 'list' subcommand to output recent entries."""
        top_str = lexer.next()
        top = None
        if top_str:
            try:
                top = int(top_str)
            except ValueError:
                return f"Error: Invalid 'top' value '{top_str}'"

        return state.journal_manager.get_entries(top)

    def delete_subcommand(self, lexer: Lexer, state: State) -> Any:
        """Handle the 'delete' subcommand to remove an entry."""
        identifier_parts = []
        while True:
            part = lexer.next()
            if part is None:
                break
            identifier_parts.append(part)

        if not identifier_parts:
            return "Error: Please provide a title or index to delete."

        identifier = " ".join(identifier_parts)
        console = state.get("console")
        if console and not console.confirm(f"Delete journal entry '{identifier}'?"):
            return "Cancelled."

        if state.journal_manager.delete_entry(identifier):
            return f"Journal entry '{identifier}' deleted."
        else:
            return f"Error: Journal entry '{identifier}' not found."

    def help(self):
        """Print exactly how to use the journal command."""
        console = Console()
        console.print(
            "[bold cyan]journal[/bold cyan]|[bold cyan]j[/bold cyan] [bold]add[/bold] "
            "\\[[italic]title[/italic]] - adds a journal entry with optional title"
        )
        console.print(
            "[bold cyan]journal[/bold cyan]|[bold cyan]j[/bold cyan] [bold]list[/bold] "
            "\\[[italic]top[/italic]] - lists journal entries optionally up to the last"
        )
        console.print(
            "[bold cyan]journal[/bold cyan]|[bold cyan]j[/bold cyan] "
            "[bold]delete[/bold]|[bold]del[/bold] [italic]<identifier>[/italic] - "
            "deletes journal entry by identifier (index or title)"
        )
