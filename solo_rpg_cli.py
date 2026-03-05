import traceback
from collections import deque
from pathlib import Path
from typing import Any

from prompt_toolkit import PromptSession

from lib.command import Command, CommandRegistry
from lib.history import History
from lib.lexer import Lexer
from lib.pretty import PrettyPrinter, PrettyPrinterRegistry
from lib.state import State


class REPLEnvironment:
    def __init__(self):
        self.session = PromptSession()
        self.state = State()
        self.history = History()
        self.command_registry = CommandRegistry()
        self.pretty_printer_registry = PrettyPrinterRegistry()
        self._quit_requested = False
        self._save_result = True

    def run(self):
        # register help command and aliases
        self.command_registry.register(
            Command.from_impl(
                "help",
                ["h"],
                "Show help for a command",
                self.help_command,
                self.help_help,
            )
        )
        # register exit command and aliases
        self.command_registry.register(
            Command.from_impl(
                "exit",
                ["quit", "bye"],
                "Exit the REPL",
                self.exit_command,
                self.exit_help,
            )
        )
        # register last command and aliases
        self.command_registry.register(
            Command.from_impl(
                "last",
                ["_"],
                "Get the result of the last command",
                self.last_command,
                self.last_help,
            )
        )
        self.command_registry.register_directory(Path("lib/commands"))

        self.pretty_printer_registry.register_directory(Path("lib/pretty_printers"))

        while True:
            self._save_result = True
            try:
                text = self.read()
                lexer = Lexer(text)
                result = self.execute(lexer)
                if self._save_result and result is not None:
                    self.history.add(text, result)
                self.print(result)
                if self._quit_requested:
                    break
            except KeyboardInterrupt:
                self._quit_requested = True
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
                continue
            if self._quit_requested:
                break

    def read(self):
        return self.session.prompt("> ")

    def execute(self, lexer: Lexer) -> Any:
        cmd = lexer.next()
        if cmd is None:
            return None
        command = self.command_registry.lookup_command(cmd)
        if command is None:
            print(f"Command '{cmd}' not found")
            return None
        try:
            result = command.execute(lexer, self.state)
        except SyntaxError as e:
            print(e)
            command.help()
            return None
        return result

    def print(self, result: Any) -> None:
        self.pretty_printer_registry.print(result)

    def exit_command(self, lexer: Lexer, state: State) -> Any:
        self._quit_requested = True
        return None

    def exit_help(self):
        print("exit|quit|bye - Exit the REPL")

    def help_command(self, lexer: Lexer, state: State) -> Any:
        command_name = lexer.next()
        if command_name is None:
            self.command_registry.help()
            return None
        command = self.command_registry.lookup_command(command_name)
        if command is None:
            print(f"Command '{command_name}' not found")
            self.command_registry.help()
            return None
        command.help()
        return None

    def help_help(self):
        print("help [command] - Show help for a command")

    def last_command(self, lexer: Lexer, state: State) -> Any:
        # was an offset provided
        offset_str = lexer.next()
        if offset_str is None:
            # return all last results
            return self.history.get_all()
        else:
            offset = int(offset_str)
            return self.history.get(offset)

    def last_help(self):
        print("last [offset] - Get the result of the last command")


if __name__ == "__main__":
    repl = REPLEnvironment()
    repl.run()
    print("Bye!")
