from typing import Optional

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
        # print a summary of all commands
        for command in self.commands:
            print(f"{command.command} - {command.description}")
