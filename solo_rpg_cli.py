import traceback
from typing import Any

from prompt_toolkit import PromptSession

from lib.command import Command, CommandRegistry
from lib.lexer import Lexer
from lib.state import State

QUIT_REQUESTED = "__quit_requested"


class REPLEnvironment:
    def __init__(self):
        self.session = PromptSession()
        self.state = State()
        self.command_registry = CommandRegistry()

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

        while True:
            try:
                text = self.read()
                lexer = Lexer(text)
                result = self.execute(lexer)
                self.print(result)
                if self.state.get(QUIT_REQUESTED):
                    break
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
                continue

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
        result = command.execute(lexer, self.state)
        return result

    def print(self, result: Any) -> None:
        if result is None:
            return
        print(result)

    def exit_command(self, lexer: Lexer, state: State) -> Any:
        self.state.set(QUIT_REQUESTED, True)
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


if __name__ == "__main__":
    repl = REPLEnvironment()
    repl.run()
    print("Bye!")
