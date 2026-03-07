from typing import Any

from lib.command import Command
from lib.lexer import Lexer
from lib.state import State


class MacroCommand(Command):
    def __init__(self):
        super().__init__()
        self.command = "macro"
        self.aliases = ["macros"]
        self.description = "Manage macros"

    def execute(self, lexer: Lexer, state: State) -> Any:
        subcommand = lexer.next()
        if subcommand is None or subcommand == "list":
            return self.do_list(state)
        elif subcommand == "reload":
            return self.do_reload(state)
        else:
            raise SyntaxError(
                f"Unknown macro subcommand: {subcommand}\nUsage: macro [list|reload]"
            )

    def do_list(self, state: State) -> Any:
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

    def do_reload(self, state: State) -> Any:
        manager = getattr(state, "macro_manager", None)
        if not manager:
            print("Macro system not initialized.")
            return None

        manager.load_macros()
        print("Macros reloaded.")
        return None

    def help(self) -> None:
        print("macro [list|reload] - Manage macros")
        print("  list - List all macros")
        print("  reload - Reload macros from disk")
