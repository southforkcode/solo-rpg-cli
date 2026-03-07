from typing import Any

from lib.core.state import State
from lib.presentation.command import Command
from lib.presentation.lexer import Lexer


class MacroCommand(Command):
    """Command to manage global and local macros."""

    def __init__(self) -> None:
        """Initialize the macro command."""
        super().__init__()
        self.command = "macro"
        self.aliases = ["macros"]
        self.description = "Manage macros"

    def execute(self, lexer: Lexer, state: State) -> object:
        """Execute the macro command with the given argument state."""
        subcommand = lexer.next()
        if subcommand is None or subcommand == "list":
            return self.do_list(state)
        elif subcommand == "reload":
            return self.do_reload(state)
        else:
            raise SyntaxError(
                f"Unknown macro subcommand: {subcommand}\nUsage: macro [list|reload]"
            )

    def do_list(self, state: State) -> object:
        """List all available macros."""
        manager = getattr(state, "macro_manager", None)
        if not manager:
            print("Macro system not initialized.")
            return None

        macros = manager.list_macros()
        if not macros:
            print("No macros defined.")
            return None

        print("Macros:")
        for m in macros:
            scope = "Global" if m.is_global else "Local"
            args_str = " ".join(
                [
                    f"{p.name}:{p.type_hint}{'=' + p.default if p.default else ''}"
                    for p in m.params
                ]
            )
            print(f"  {m.name} {args_str} ({scope})")

        return None

    def do_reload(self, state: State) -> object:
        """Reload the macro definitions from disk."""
        manager = getattr(state, "macro_manager", None)
        if not manager:
            print("Macro system not initialized.")
            return None

        manager.load_macros()
        print("Macros reloaded.")
        return None

    def help(self) -> None:
        """Display help documentation for the macro command."""
        print("macro [list|reload] - Manage macros")
        print("  list - List all macros")
        print("  reload - Reload macros from disk")
