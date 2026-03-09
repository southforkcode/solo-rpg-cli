import unittest
from unittest.mock import MagicMock, patch

from lib.core.journal import JournalManager
from lib.core.journey import Journey, JourneyManager
from lib.core.state import State
from lib.presentation.commands.journey_command import JourneyCommand
from lib.presentation.console import Console
from lib.presentation.lexer import Lexer


class TestJourneyCommand(unittest.TestCase):
    def setUp(self):
        self.mock_journey_manager = MagicMock(spec=JourneyManager)
        self.mock_journal_manager = MagicMock(spec=JournalManager)
        
        self.mock_state = MagicMock(spec=State)
        self.mock_state.journey_manager = self.mock_journey_manager
        self.mock_state.journal_manager = self.mock_journal_manager
        self.mock_console = MagicMock(spec=Console)
        self.mock_state.get.return_value = self.mock_console

        self.command = JourneyCommand()
        
    def test_help_no_subcommand(self):
        lexer = Lexer("")
        result = self.command.execute(lexer, self.mock_state)
        self.assertIsNone(result)

    def test_unknown_subcommand(self):
        lexer = Lexer("jump")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Error: Unknown journey subcommand 'jump'")

    # --- Start Subcommand Tests ---
    def test_start_no_title(self):
        lexer = Lexer("start")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Error: Please provide a journey title.")

    @patch("lib.presentation.commands.journey_command.prompt")
    def test_start_success(self, mock_prompt):
        lexer = Lexer('start "To the Mountain"')
        # Mocking the interactive prompts
        # sequence: desc line 1, EOF (ends desc), difficulty, steps
        mock_prompt.side_effect = ["Walking to the big peak.", "...", "Hard", "10"]
        
        result = self.command.execute(lexer, self.mock_state)
        
        self.assertEqual(result, 'Journey "To the Mountain" started.')
        self.mock_journey_manager.add_journey.assert_called_once_with(
            "To the Mountain", "Walking to the big peak.", "Hard", 10
        )
        self.mock_journal_manager.add_entry.assert_called_once()
        journal_arg = self.mock_journal_manager.add_entry.call_args[0][0]
        self.assertEqual(journal_arg.title, "Started Journey: To the Mountain")
        self.assertEqual(journal_arg.content, "Walking to the big peak.")

    @patch("lib.presentation.commands.journey_command.prompt")
    def test_start_keyboard_interrupt(self, mock_prompt):
        lexer = Lexer('start A test')
        mock_prompt.side_effect = KeyboardInterrupt()
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Journey cancelled.")

    @patch("lib.presentation.commands.journey_command.prompt")
    def test_start_invalid_steps(self, mock_prompt):
        lexer = Lexer("start test")
        mock_prompt.side_effect = ["...", "Hard", "abc"]
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Error: Steps must be an integer.")

    # --- List Subcommand Tests ---
    def test_list_default(self):
        lexer = Lexer("list")
        self.mock_journey_manager.list_journeys.return_value = "Mocked list active"
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Mocked list active")
        self.mock_journey_manager.list_journeys.assert_called_once_with("active")
        
    def test_list_paused(self):
        lexer = Lexer("list -paused")
        self.mock_journey_manager.list_journeys.return_value = "Mocked list paused"
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Mocked list paused")
        self.mock_journey_manager.list_journeys.assert_called_once_with("paused")

    # --- Progress Subcommand Tests ---
    def test_progress_no_identifier(self):
        lexer = Lexer("progress")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Error: Please provide a journey identifier.")
        
    def test_progress_not_found(self):
        lexer = Lexer("progress unknown")
        self.mock_journey_manager.get_journey.return_value = None
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, 'Error: Journey "unknown" not found.')

    def test_progress_not_active(self):
        lexer = Lexer("progress known")
        mock_journey = MagicMock(spec=Journey)
        mock_journey.state = "paused"
        self.mock_journey_manager.get_journey.return_value = mock_journey
        
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Error: Journey is not active (paused).")

    @patch("lib.presentation.commands.journey_command.prompt")
    def test_progress_success(self, mock_prompt):
        lexer = Lexer('progress "The Woods"')
        mock_journey = MagicMock(spec=Journey)
        mock_journey.title = "The Woods"
        mock_journey.state = "active"
        mock_journey.progress = 2
        mock_journey.steps = 5
        self.mock_journey_manager.get_journey.return_value = mock_journey
        mock_prompt.return_value = "Advanced one milestone."
        
        result = self.command.execute(lexer, self.mock_state)
        self.assertIsNone(result)
        self.assertEqual(mock_journey.progress, 3)
        self.mock_journey_manager.update_journey.assert_called_once_with(mock_journey)
        self.mock_journal_manager.add_entry.assert_called_once()
        journal_arg = self.mock_journal_manager.add_entry.call_args[0][0]
        self.assertEqual(journal_arg.title, "Journey Progressed: The Woods")

    @patch("lib.presentation.commands.journey_command.prompt")
    def test_progress_completion(self, mock_prompt):
        lexer = Lexer('progress "To completion"')
        mock_journey = MagicMock(spec=Journey)
        mock_journey.title = "To completion"
        mock_journey.state = "active"
        mock_journey.progress = 4
        mock_journey.steps = 5
        self.mock_journey_manager.get_journey.return_value = mock_journey
        mock_prompt.return_value = "Final step."
        
        self.command.execute(lexer, self.mock_state)
        self.assertEqual(mock_journey.progress, 5)
        self.assertEqual(mock_journey.state, "completed")
        self.mock_journal_manager.add_entry.assert_called_once()
        journal_arg = self.mock_journal_manager.add_entry.call_args[0][0]
        self.assertEqual(
            journal_arg.title, "Journey Progressed: To completion (Completed)"
        )

    # --- State Change Combinations (pause/resume/stop/complete) ---
    def test_state_change_pause(self):
        lexer = Lexer("pause MyJourney")
        mock_journey = MagicMock(spec=Journey)
        mock_journey.title = "MyJourney"
        mock_journey.progress = 1
        mock_journey.steps = 2
        self.mock_journey_manager.get_journey.return_value = mock_journey
        
        with patch(
            "lib.presentation.commands.journey_command.prompt",
            return_value="Need rest"
        ):
            self.command.execute(lexer, self.mock_state)
            
        self.assertEqual(mock_journey.state, "paused")
        self.mock_journey_manager.update_journey.assert_called_once_with(mock_journey)
        self.mock_journal_manager.add_entry.assert_called_once()

    def test_state_change_resume(self):
        lexer = Lexer("resume MyJourney")
        mock_journey = MagicMock(spec=Journey)
        mock_journey.title = "MyJourney"
        mock_journey.steps = None
        mock_journey.progress = 0
        self.mock_journey_manager.get_journey.return_value = mock_journey
        
        with patch(
            "lib.presentation.commands.journey_command.prompt",
            return_value="Continuing"
        ):
            self.command.execute(lexer, self.mock_state)
            
        self.assertEqual(mock_journey.state, "active")

    # --- Remove Subcommand Tests ---
    def test_remove_no_identifier(self):
        lexer = Lexer("rm")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Error: Please provide a journey identifier.")

    def test_remove_not_found(self):
        lexer = Lexer("rm missing")
        self.mock_journey_manager.get_journey.return_value = None
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, 'Error: Journey "missing" not found.')

    def test_remove_console_confirm_yes(self):
        lexer = Lexer("rm test")
        mock_journey = MagicMock(spec=Journey)
        mock_journey.id = 123
        mock_journey.title = "test"
        mock_journey.steps = None
        mock_journey.progress = 0
        self.mock_journey_manager.get_journey.return_value = mock_journey
        self.mock_console.confirm.return_value = True
        
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, 'Journey "test" removed.')
        self.mock_journey_manager.remove_journey.assert_called_once_with("123")
        
    def test_remove_console_confirm_no(self):
        lexer = Lexer("rm test")
        mock_journey = MagicMock(spec=Journey)
        mock_journey.title = "test"
        mock_journey.steps = None
        mock_journey.progress = 0
        self.mock_journey_manager.get_journey.return_value = mock_journey
        self.mock_console.confirm.return_value = False
        
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Cancelled.")
        self.mock_journey_manager.remove_journey.assert_not_called()

    # --- Autocomplete Tests ---
    def test_get_completions_empty(self):
        self.assertEqual(self.command.get_completions("", self.mock_state), [])
        
    def test_get_completions_verbs(self):
        result = self.command.get_completions("journey ", self.mock_state)
        self.assertIn("start", result)
        self.assertIn("list", result)
        self.assertIn("pause", result)

    def test_get_completions_partial_verb(self):
        result = self.command.get_completions("journey s", self.mock_state)
        self.assertEqual(set(result), {"start", "stop"})
        
    def test_get_completions_journey_list(self):
        mock_journey = MagicMock(spec=Journey)
        mock_journey.title = "Epic Quest"
        mock_journey.id = 1
        self.mock_journey_manager.list_journeys.return_value = [mock_journey]
        
        result = self.command.get_completions("journey progress ", self.mock_state)
        self.assertIn('"Epic Quest"', result)
        self.assertIn("1", result)

    def test_get_completions_journeyPrefix(self):
        mock_journey = MagicMock(spec=Journey)
        mock_journey.title = "Epic Quest"
        mock_journey.id = 1
        self.mock_journey_manager.list_journeys.return_value = [mock_journey]
        
        result = self.command.get_completions("journey pause ep", self.mock_state)
        self.assertEqual(result, ['"Epic Quest"'])

    def test_get_completions_journey_state_filters(self):
        # Progress filters active
        self.command.get_completions("journey progress ", self.mock_state)
        self.mock_journey_manager.list_journeys.assert_called_with("active")
        
        # Resume filters paused
        self.command.get_completions("journey resume ", self.mock_state)
        self.mock_journey_manager.list_journeys.assert_called_with("paused")

if __name__ == '__main__':
    unittest.main()
