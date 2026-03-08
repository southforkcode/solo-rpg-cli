import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from lib.core.state import StateFactory
from lib.presentation.commands.oracle_command import OracleCommand
from lib.presentation.lexer import Lexer


class TestOracleCommand(unittest.TestCase):
    def setUp(self):
        self.command = OracleCommand()
        self.temp_dir = TemporaryDirectory()
        self.state = StateFactory.create(base_dir=Path(self.temp_dir.name))

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("lib.presentation.commands.oracle_command.random.randint")
    def test_basic_question_yes(self, mock_randint):
        mock_randint.return_value = 1
        lexer = Lexer('"Is it raining?"')
        result = self.command.execute(lexer, self.state)
        self.assertEqual(result, "Oracle: Yes (Question: Is it raining?)")
        mock_randint.assert_called_once_with(1, 100)

    @patch("lib.presentation.commands.oracle_command.random.randint")
    def test_basic_question_no(self, mock_randint):
        mock_randint.return_value = 51  # 50/50 default
        lexer = Lexer('"Is it raining?"')
        result = self.command.execute(lexer, self.state)
        self.assertEqual(result, "Oracle: No (Question: Is it raining?)")

    @patch("lib.presentation.commands.oracle_command.random.randint")
    def test_custom_odds(self, mock_randint):
        mock_randint.return_value = 75
        lexer = Lexer('"Is it raining?" --odds likely')
        result = self.command.execute(lexer, self.state)
        self.assertEqual(result, "Oracle: Yes (Question: Is it raining?)")

        mock_randint.return_value = 76
        lexer = Lexer('"Is it raining?" --odds likely')
        result = self.command.execute(lexer, self.state)
        self.assertEqual(result, "Oracle: No (Question: Is it raining?)")

    def test_missing_odds_value(self):
        lexer = Lexer('"Is it raining?" --odds')
        with self.assertRaises(SyntaxError):
            self.command.execute(lexer, self.state)

    @patch("lib.presentation.commands.oracle_command.random.randint")
    def test_unquoted_question(self, mock_randint):
        mock_randint.return_value = 1
        lexer = Lexer("Is the chest locked?")
        result = self.command.execute(lexer, self.state)
        self.assertEqual(result, "Oracle: Yes (Question: Is the chest locked?)")

    def test_no_arguments_dumps_table(self):
        lexer = Lexer("")
        result = self.command.execute(lexer, self.state)
        self.assertTrue(result.startswith("Oracle Probability Table:"))
        self.assertIn("certain: 90%", result)
        self.assertIn("impossible: 10%", result)

    @patch("lib.presentation.commands.oracle_command.random.randint")
    def test_config_override(self, mock_randint):
        # Create a mock oracle.json
        config_path = self.state.base_dir / "oracle.json"
        with open(config_path, "w") as f:
            json.dump({"weird_odds": 99}, f)

        mock_randint.return_value = 99
        lexer = Lexer("--odds weird_odds")
        result = self.command.execute(lexer, self.state)
        self.assertEqual(result, "Oracle: Yes")

    @patch("lib.presentation.commands.oracle_command.random.randint")
    def test_config_fallback_unknown(self, mock_randint):
        mock_randint.return_value = 50
        lexer = Lexer("--odds not_real")
        result = self.command.execute(lexer, self.state)
        # Should fallback to 50/50
        self.assertEqual(result, "Oracle: Yes")


if __name__ == "__main__":
    unittest.main()
