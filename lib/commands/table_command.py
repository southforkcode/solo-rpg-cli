import time
from typing import Any

from lib.command import Command
from lib.lexer import Lexer
from lib.state import State


class TableCommand(Command):
    """Command to interact with random tables."""

    def __init__(self) -> None:
        """Initialize the table command."""
        super().__init__()
        self.command = "table"
        self.aliases = ["tables"]
        self.description = "Roll on random tables or list them"

    def execute(self, lexer: Lexer, state: State) -> Any:
        """Execute the table command with the given argument state."""
        subcommand = lexer.next()

        if subcommand == "list":
            return self.do_list(state)
        elif subcommand == "roll":
            table_name = lexer.next()
            if not table_name:
                raise SyntaxError("Usage: table roll <table_name>")
            return self.do_roll(table_name, state)
        else:
            raise SyntaxError(
                f"Unknown table subcommand: {subcommand}\nUsage: table [list|roll <name>]"
            )

    def do_list(self, state: State) -> Any:
        """List all available tables."""
        manager = getattr(state, "table_manager", None)
        if not manager:
            print("Table system not initialized.")
            return None

        tables = manager.list_tables()
        if not tables:
            print("No tables available.")
            return None

        print("Available tables:")
        for tbl in tables:
            print(f"  - {tbl}")

        return None

    def do_roll(self, table_name: str, state: State) -> Any:
        """Roll on a given table and journal the result."""
        manager = getattr(state, "table_manager", None)
        if not manager:
            print("Table system not initialized.")
            return None

        result = manager.roll(table_name)
        if result is None:
            print(f"Table '{table_name}' not found or is empty.")
            return None

        print(f"Result: {result}")

        # Add to journal
        from lib.journal import JournalEntry

        entry = JournalEntry(
            title=f"Rolled on table '{table_name}'",
            content=result,
            timestamp=time.time(),
        )
        state.journal_manager.add_entry(entry)

        return result

    def help(self) -> None:
        """Display help documentation for the table command."""
        print("table [list|roll <table_name>] - Interact with random tables")
        print("  list - List all available tables")
        print("  roll <table_name> - Roll a random item from the given table")
