import unittest
from unittest.mock import MagicMock

from lib.lexer import Lexer
from lib.state import State
from lib.commands.summary_command import SummaryCommand, GameSummary


class TestSummaryCommand(unittest.TestCase):
    def test_summary_command_execute(self):
        state = MagicMock(spec=State)
        state.journal_manager = MagicMock()
        state.journey_manager = MagicMock()
        
        state.journal_manager.get_entries.return_value = ["mock_journal"]
        state.journey_manager.list_journeys.return_value = ["mock_journey"]

        command = SummaryCommand()
        lexer = Lexer("summary")
        result = command.execute(lexer, state)

        state.journal_manager.get_entries.assert_called_once_with(5)
        state.journey_manager.list_journeys.assert_called_once_with("active")
        
        self.assertIsInstance(result, GameSummary)
        self.assertEqual(result.journals, ["mock_journal"])
        self.assertEqual(result.journeys, ["mock_journey"])
