import importlib.util
import inspect
import os
import sys
from pathlib import Path
from typing import Any, Callable, Optional

from lib.lexer import Lexer
from lib.state import State


class Command:
    @classmethod
    def from_impl(
        cls,
        command: str,
        aliases: list[str],
        description: str,
        exec_impl: Callable[[Lexer, State], Any],
        help_impl: Callable[[], None],
    ):
        command_obj = cls()
        command_obj.command = command
        command_obj.aliases = aliases
        command_obj.description = description
        command_obj.exec_impl = exec_impl
        command_obj.help_impl = help_impl
        return command_obj

    def __init__(self):
        self.command = ""
        self.aliases = []
        self.description = ""
        self.exec_impl: Callable[[Lexer, State], Any] = None
        self.help_impl: Callable[[], None] = None

    def execute(self, lexer: Lexer, state: State) -> Any:
        if self.exec_impl is not None:
            return self.exec_impl(lexer, state)
        raise NotImplementedError

    def help(self) -> None:
        if self.help_impl is not None:
            self.help_impl()
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

    def register_directory(self, directory: Path) -> None:
        for filename in os.listdir(directory):
            if filename.endswith(".py"):
                # load module and find all Command instances
                module_name = "commands." + Path(filename).stem
                spec = importlib.util.spec_from_file_location(
                    module_name, directory / filename
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                classes = inspect.getmembers(module, inspect.isclass)
                for _, obj in classes:
                    if issubclass(obj, Command) and obj != Command:
                        self.register(obj())

    def lookup_command(self, command_or_alias: str) -> Optional[Command]:
        return self.command_map.get(command_or_alias) or self.alias_map.get(
            command_or_alias
        )

    def help(self):
        # print a summary of all commands
        for command in self.commands:
            print(f"{command.command} - {command.description}")
