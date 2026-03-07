import time
import traceback
from pathlib import Path
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from lib.command import Command, CommandRegistry
from lib.history import History
from lib.lexer import Lexer
from lib.macro import MacroEvaluator, MacroManager
from lib.pretty import PrettyPrinterRegistry
from lib.state import State


class REPLEnvironment:
    def __init__(self, gamedir: Path):
        self.gamedir = gamedir
        self._session: PromptSession | None = None
        self.state = State(base_dir=gamedir)
        self.state.set("gamedir", gamedir)
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
                if result is not None:
                    self.print(result)
                if self._quit_requested:
                    break
            except KeyboardInterrupt:
                self._quit_requested = True
            except EOFError:
                self._quit_requested = True
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
                continue
            if self._quit_requested:
                break

    @property
    def session(self) -> PromptSession:
        if self._session is None:
            self._session = PromptSession(
                history=FileHistory(str(self.gamedir / "history"))
            )
        return self._session

    def read(self):
        import sys
        # Note: In Pytest/Behave environments stdout and stdin are often mocks and not true TTYs.
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            print("> ", end="", flush=True)
            line = sys.stdin.readline()
            if not line:
                raise EOFError()
            return line.rstrip("\n")
        return self.session.prompt("> ")

    def execute(self, lexer: Lexer) -> Any:
        cmd = lexer.next()
        if cmd is None:
            return None

        if cmd.startswith("//") or cmd.startswith("/"):
            is_journal = cmd.startswith("//")
            macro_name = cmd[2:] if is_journal else cmd[1:]

            if not macro_name and is_journal:
                # user typed just "//", means journal the last command
                last_result = self.history.get(0)
                if last_result is not None:
                    # we need to add to journal. We can just invoke Journal.add
                    from lib.journal import JournalEntry

                    self.state.journal_manager.add_entry(
                        JournalEntry(
                            title="Last Result",
                            content=str(last_result),
                            timestamp=time.time(),
                        )
                    )
                    print("Added last result to journal.")
                else:
                    print("No previous valid result to journal.")
                return None

            macro = self.state.macro_manager.get_macro(macro_name)
            if macro is None:
                print(f"Macro '{macro_name}' not found.")
                return None

            # extract args
            args = []
            while True:
                arg = lexer.next()
                if arg is None:
                    break
                args.append(arg)

            # setup callbacks
            def cb_exec(text: str) -> Any:
                sub_lexer = Lexer(text)
                return self.execute(sub_lexer)

            def cb_roll(text: str) -> Any:
                sub_lexer = Lexer(text)
                from lib.commands.roll_command import RollCommand

                # fake state execution
                cmd = RollCommand()
                return cmd.execute(sub_lexer, self.state)

            evaluator = MacroEvaluator(macro, args, cb_exec, cb_roll)
            try:
                ret = evaluator.run()
            except Exception as e:
                print(f"Macro execution failed: {e}")
                return None

            if is_journal:
                from lib.journal import JournalEntry

                # join outputs or use return value
                final_output = (
                    str(ret) if ret is not None else "\n".join(evaluator.outputs)
                )
                if final_output:
                    self.state.journal_manager.add_entry(
                        JournalEntry(
                            title=f"Macro {macro_name}",
                            content=final_output,
                            timestamp=time.time(),
                        )
                    )
                    print("Added macro output to journal.")

            return ret

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
