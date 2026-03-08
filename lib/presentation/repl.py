import time
import traceback
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from lib.core.macro import MacroEvaluator
from lib.core.state import State
from lib.infrastructure.history import History
from lib.presentation.command import Command, CommandRegistry
from lib.presentation.lexer import Lexer
from lib.presentation.pretty import PrettyPrinterRegistry


class _HelpCommand(Command):
    """Command to display help information for other commands or list all commands."""

    def __init__(self, repl):
        super().__init__()
        self.command = "help"
        self.aliases = ["h"]
        self.description = "Show help for a command"
        self.repl = repl

    def execute(self, lexer: Lexer, state: State) -> object:
        """Execute the help command, showing general help or specific command help."""
        command_name = lexer.next()
        if command_name is None:
            self.repl.command_registry.help()
            return None
        command = self.repl.command_registry.lookup_command(command_name)
        if command is None:
            print(f"Command '{command_name}' not found")
            self.repl.command_registry.help()
            return None
        command.help()
        return None

    def help(self) -> None:
        """Print the help documentation for the help command itself."""
        print("help [command] - Show help for a command")


class _ExitCommand(Command):
    """Command to cleanly exit the REPL environment."""

    def __init__(self, repl):
        super().__init__()
        self.command = "exit"
        self.aliases = ["quit", "bye"]
        self.description = "Exit the REPL"
        self.repl = repl

    def execute(self, lexer: Lexer, state: State) -> object:
        """Execute the exit command, signaling the REPL to terminate."""
        self.repl._quit_requested = True
        return None

    def help(self) -> None:
        """Print the help documentation for the exit command."""
        print("exit|quit|bye - Exit the REPL")


class _LastCommand(Command):
    """Command to retrieve the result of the previously executed command."""

    def __init__(self, repl):
        super().__init__()
        self.command = "last"
        self.aliases = ["_"]
        self.description = "Get the result of the last command"
        self.repl = repl

    def execute(self, lexer: Lexer, state: State) -> object:
        """Execute the last command, fetching results from command history."""
        offset_str = lexer.next()
        if offset_str is None:
            return self.repl.history.get_all()
        else:
            offset = int(offset_str)
            return self.repl.history.get(offset)

    def help(self) -> None:
        """Print the help documentation for the last command."""
        print("last [offset] - Get the result of the last command")


class InputReader:
    def __init__(self, gamedir: Path):
        self.gamedir = gamedir
        self._session: PromptSession | None = None

    @property
    def session(self) -> PromptSession:
        if self._session is None:
            self._session = PromptSession(
                history=FileHistory(str(self.gamedir / "history"))
            )
        return self._session

    def read(self) -> str:
        import sys
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            print("> ", end="", flush=True)
            line = sys.stdin.readline()
            if not line:
                raise EOFError()
            return line.rstrip("\n")
        return self.session.prompt("> ")


class CommandExecutor:
    def __init__(self, repl_env: "REPLEnvironment"):
        self.repl = repl_env

    def execute(self, lexer: Lexer) -> object:
        cmd = lexer.next()
        if cmd is None:
            return None

        if cmd.startswith("//") or cmd.startswith("/"):
            is_journal = cmd.startswith("//")
            macro_name = cmd[2:] if is_journal else cmd[1:]

            if not macro_name and is_journal:
                last_result = self.repl.history.get(0)
                if last_result is not None:
                    from lib.core.journal import JournalEntry
                    self.repl.state.journal_manager.add_entry(
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

            macro = self.repl.state.macro_manager.get_macro(macro_name)
            if macro is None:
                print(f"Macro '{macro_name}' not found.")
                return None

            args = []
            while True:
                arg = lexer.next()
                if arg is None:
                    break
                args.append(arg)

            def cb_exec(text: str) -> object:
                sub_lexer = Lexer(text)
                return self.execute(sub_lexer)

            def cb_roll(text: str) -> object:
                sub_lexer = Lexer(text)
                from lib.presentation.commands.roll_command import RollCommand
                cmd_obj = RollCommand()
                return cmd_obj.execute(sub_lexer, self.repl.state)

            evaluator = MacroEvaluator(
                macro,
                args,
                cb_exec,
                cb_roll,
                global_vars=self.repl.state.variable_manager.get_all(),
            )
            try:
                ret = evaluator.run()
            except Exception as e:
                print(f"Macro execution failed: {e}")
                return None

            if is_journal:
                from lib.core.journal import JournalEntry
                final_output = (
                    str(ret) if ret is not None else "\n".join(evaluator.outputs)
                )
                if final_output:
                    self.repl.state.journal_manager.add_entry(
                        JournalEntry(
                            title=f"Macro {macro_name}",
                            content=final_output,
                            timestamp=time.time(),
                        )
                    )
                    print("Added macro output to journal.")

            return ret

        command = self.repl.command_registry.lookup_command(cmd)
        if command is None:
            print(f"Command '{cmd}' not found")
            return None
        try:
            result = command.execute(lexer, self.repl.state)
        except SyntaxError as e:
            print(e)
            command.help()
            return None
        return result


class REPLEnvironment:
    def __init__(self, gamedir: Path, state: State):
        self.gamedir = gamedir
        self.state = state
        self.state.set("gamedir", gamedir)
        self.history = History()
        self.command_registry = CommandRegistry()
        self.pretty_printer_registry = PrettyPrinterRegistry()
        self.input_reader = InputReader(gamedir)
        self.executor = CommandExecutor(self)
        self._quit_requested = False
        self._save_result = True

    def run(self):
        self.command_registry.register(_HelpCommand(self))
        self.command_registry.register(_ExitCommand(self))
        self.command_registry.register(_LastCommand(self))

        while True:
            self._save_result = True
            try:
                text = self.input_reader.read()
                lexer = Lexer(text)
                result = self.executor.execute(lexer)
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

    def print(self, result: object) -> None:
        self.pretty_printer_registry.print(result)
