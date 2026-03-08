from rich.console import Console

from lib.core.state import State
from lib.presentation.command import Command
from lib.presentation.lexer import Lexer


class TableCommand(Command):
    """Command to interact with random tables."""

    def __init__(self) -> None:
        """Initialize the table command."""
        super().__init__()
        self.command = "table"
        self.aliases = ["tables"]
        self.description = "Roll on random tables or list them"

    def get_completions(self, text_before_cursor: str, state: State) -> list[str]:
        """Return a list of autocomplete suggestions."""
        words = text_before_cursor.split()
        if not words:
            return []

        is_new_word = text_before_cursor.endswith(" ")
        verbs = ["list", "roll"]

        if len(words) == 1 and not is_new_word:
            return []

        if len(words) == 1 and is_new_word:
            return verbs

        if len(words) == 2 and not is_new_word:
            prefix = words[1].lower()
            return [v for v in verbs if v.startswith(prefix)]

        verb = words[1].lower()
        if verb == "roll":
            manager = getattr(state, "table_manager", None)
            tables = manager.list_tables() if manager else []
            tables = [f'"{t}"' if " " in t else t for t in tables]

            if len(words) == 2 and is_new_word:
                return tables

            if len(words) == 3 and not is_new_word:
                prefix = words[2].lower()
                clean_prefix = prefix.strip("\"'")
                return [
                    t for t in tables if t.strip("\"'").lower().startswith(clean_prefix)
                ]

        return []

    def execute(self, lexer: Lexer, state: State) -> object:
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
                f"Unknown table subcommand: {subcommand}\n"
                "Usage: table [list|roll <name>]"
            )

    def do_list(self, state: State) -> object:
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

    def do_roll(self, table_name: str, state: State) -> object:
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


        return result

    def help(self) -> None:
        """Display help documentation for the table command."""
        console = Console()
        console.print(
            "[bold cyan]table[/bold cyan] \\[[bold]list[/bold]|[bold]roll[/bold] "
            "[italic]<table_name>[/italic]] - Interact with random tables"
        )
        console.print("  [bold]list[/bold] - List all available tables")
        console.print(
            "  [bold]roll[/bold] [italic]<table_name>[/italic] - Roll a random "
            "item from the given table"
        )
