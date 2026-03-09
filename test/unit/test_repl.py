import unittest
from pathlib import Path

from lib.core.state import State
from lib.presentation.console import MockConsole
from lib.presentation.repl import REPLEnvironment


class DummyCommand:
    def __init__(self):
        self.command = "dummy"
        self.aliases = ["d"]
        self.description = "Dummy command"

    def execute(self, lexer, state):
        return "Dummy Result"

    def help(self):

        print("dummy - dummy help")


class TestREPLEnvironment(unittest.TestCase):
    def setUp(self):
        self.gamedir = Path("test_gamedir")
        self.gamedir.mkdir(parents=True, exist_ok=True)
        # Ensure state provides necessary managers
        from lib.core.journal import JournalManager
        from lib.core.journey import JourneyManager
        from lib.core.macro import MacroManager
        from lib.core.settings import SettingsManager
        from lib.core.table import TableManager
        from lib.core.variable import VariableManager
        from unittest.mock import MagicMock

        self.state = State(
            base_dir=self.gamedir,
            journal_manager=JournalManager(self.gamedir),
            journey_manager=JourneyManager(self.gamedir),
            macro_manager=MacroManager(self.gamedir),
            music_manager=MagicMock(),
            settings_manager=SettingsManager(self.gamedir),
            table_manager=TableManager(self.gamedir, SettingsManager(self.gamedir)),
            variable_manager=VariableManager(self.gamedir),
        )

    def tearDown(self):
        import shutil

        if self.gamedir.exists():
            shutil.rmtree(self.gamedir)

    def test_exit_command(self):
        console = MockConsole(["exit"])
        repl = REPLEnvironment(self.gamedir, self.state, console=console)
        repl.run()
        self.assertTrue(repl._quit_requested)

    import io
    from unittest.mock import patch

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_help_command(self, mock_stdout):
        console = MockConsole(["help", "exit"])
        repl = REPLEnvironment(self.gamedir, self.state, console=console)
        repl.run()
        outputs_str = mock_stdout.getvalue() + " ".join(str(o) for o in console.outputs)
        self.assertIn("Show help for a command", outputs_str)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_unknown_command(self, mock_stdout):
        console = MockConsole(["unknown_cmd", "exit"])
        repl = REPLEnvironment(self.gamedir, self.state, console=console)
        repl.run()
        outputs_str = mock_stdout.getvalue() + " ".join(str(o) for o in console.outputs)
        self.assertIn("Command 'unknown_cmd' not found", outputs_str)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_last_command(self, mock_stdout):
        console = MockConsole(["dummy", "last 0", "exit"])
        repl = REPLEnvironment(self.gamedir, self.state, console=console)
        repl.command_registry.register(DummyCommand())
        repl.run()
        outputs = mock_stdout.getvalue() + "".join(str(o) for o in console.outputs)
        self.assertIn("Dummy Result", outputs)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_macro_not_found(self, mock_stdout):
        console = MockConsole(["/missing_macro", "exit"])
        repl = REPLEnvironment(self.gamedir, self.state, console=console)
        repl.run()
        outputs_str = mock_stdout.getvalue() + " ".join(str(o) for o in console.outputs)
        self.assertIn("Macro 'missing_macro' not found", outputs_str)

    def test_eof_handling(self):
        console = MockConsole([])  # Empty inputs will cause EOFError in MockConsole
        repl = REPLEnvironment(self.gamedir, self.state, console=console)
        repl.run()
        self.assertTrue(repl._quit_requested)

    def test_journal_last_result(self):
        console = MockConsole(["dummy", "//", "exit"])
        repl = REPLEnvironment(self.gamedir, self.state, console=console)
        repl.command_registry.register(DummyCommand())
        repl.run()
        entries = self.state.journal_manager.get_entries()
        self.assertTrue(any(e.title == "Last Result" for e in entries))

    def test_journal_no_last_result(self):
        import io
        from unittest.mock import patch

        console = MockConsole(["//", "exit"])
        repl = REPLEnvironment(self.gamedir, self.state, console=console)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            repl.run()
            output = mock_stdout.getvalue() + " ".join(str(o) for o in console.outputs)
            self.assertIn("No previous valid result to journal", output)
