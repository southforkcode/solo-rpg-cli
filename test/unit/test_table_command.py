import io
import sys
import tempfile
import unittest
from pathlib import Path

from lib.commands.table_command import TableCommand
from lib.lexer import Lexer
from lib.state import State


class TestTableCommand(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.tables_dir = self.base_dir / "tables"
        self.tables_dir.mkdir()

        # Add dummy tables
        (self.tables_dir / "heroes.txt").write_text(
            "Arthur\nLancelot", encoding="utf-8"
        )
        (self.tables_dir / "loot.csv").write_text(
            "Gold,100\nPotion,50", encoding="utf-8"
        )

        self.state = State(self.base_dir)
        self.state.table_manager.load_tables()
        self.command = TableCommand()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_list_subcommand(self):
        lexer = Lexer("list")

        # Test output
        captured_output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        try:
            self.command.execute(lexer, self.state)
        finally:
            sys.stdout = old_stdout

        output = captured_output.getvalue()
        self.assertIn("Available tables:", output)
        self.assertIn("heroes", output)
        self.assertIn("loot", output)

    def test_roll_subcommand(self):
        lexer = Lexer("roll heroes")

        captured_output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        try:
            result = self.command.execute(lexer, self.state)
        finally:
            sys.stdout = old_stdout

        output = captured_output.getvalue()
        self.assertIn("Result:", output)
        self.assertIn(result, ["Arthur", "Lancelot"])

        # Check journal
        entries = self.state.journal_manager.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "Rolled on table 'heroes'")
        self.assertEqual(entries[0].content, result)

    def test_roll_missing_table(self):
        lexer = Lexer("roll nonexistent")

        captured_output = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        try:
            result = self.command.execute(lexer, self.state)
        finally:
            sys.stdout = old_stdout

        output = captured_output.getvalue()
        self.assertIsNone(result)
        self.assertIn("not found", output)

    def test_roll_missing_args(self):
        lexer = Lexer("roll")
        with self.assertRaises(SyntaxError):
            self.command.execute(lexer, self.state)

    def test_invalid_subcommand(self):
        lexer = Lexer("smash")
        with self.assertRaises(SyntaxError):
            self.command.execute(lexer, self.state)

    def test_no_args(self):
        lexer = Lexer("")
        with self.assertRaises(SyntaxError):
            self.command.execute(lexer, self.state)
