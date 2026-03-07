from datetime import datetime
from typing import Any

import prompt_toolkit

from lib.command import Command
from lib.journal import JournalEntry
from lib.lexer import Lexer
from lib.state import State


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

    def execute(self, lexer: Lexer, state: State) -> Any:
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
        if state.journal_manager.delete_entry(identifier):
            return f"Journal entry '{identifier}' deleted."
        else:
            return f"Error: Journal entry '{identifier}' not found."

    def help(self):
        """Print exactly how to use the journal command."""
        print("journal|j add [title] - adds a journal entry with optional title")
        print("journal|j list [top] - lists journal entries optionally up to the last")
        print(
            "journal|j delete|del <identifier> - "
            "deletes journal entry by identifier (index or title)"
        )
