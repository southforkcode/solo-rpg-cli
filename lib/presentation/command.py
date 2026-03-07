import importlib.util
import inspect
import os
import sys
from pathlib import Path
from typing import Callable, Optional

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

    def register_directory(self, directory: Path) -> None:
        for filename in os.listdir(directory):
            if filename.endswith(".py"):
                module_name = "lib.commands." + Path(filename).stem
                spec = importlib.util.spec_from_file_location(
                    module_name, directory / filename
                )
                if spec is None or spec.loader is None:
                    continue
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
