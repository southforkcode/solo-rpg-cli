from typing import Optional

from rich.console import Console
from rich.table import Table

from lib.core.state import State
from lib.presentation.lexer import Lexer


class Command:
    def __init__(self):
        self.command = ""
        self.aliases = []
        self.description = ""

    def execute(self, lexer: Lexer, state: State) -> object:
        raise NotImplementedError

    def help(self) -> None:
        raise NotImplementedError

    def get_completions(self, text_before_cursor: str, state: State) -> list[str]:
        """
        Return a list of autocomplete suggestions based on the current input text.
        By default, returns an empty list. Commands can override this.
        """
        return []


class CommandRegistry:
    def __init__(self):
        self.commands: list[Command] = []
        self.command_map: dict[str, Command] = {}
        self.alias_map: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        assert command not in self.commands
        self.commands.append(command)
        self.command_map[command.command] = command
        for alias in command.aliases:
            assert alias not in self.alias_map
            self.alias_map[alias] = command

    def lookup_command(self, command_or_alias: str) -> Optional[Command]:
        return self.command_map.get(command_or_alias) or self.alias_map.get(
            command_or_alias
        )

    def help(self):
        console = Console()
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Command", style="cyan", width=20)
        table.add_column("Description", style="white")

        for command in self.commands:
            cmd_str = command.command
            if command.aliases:
                cmd_str += f" ({', '.join(command.aliases)})"
            table.add_row(cmd_str, command.description)

        console.print()
        console.print(table)
        console.print()
