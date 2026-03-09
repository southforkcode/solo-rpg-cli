import unittest
from unittest.mock import MagicMock

from lib.core.music import MusicPlayerProtocol
from lib.core.state import State
from lib.presentation.commands.music_command import MusicCommand
from lib.presentation.lexer import Lexer


class TestMusicCommand(unittest.TestCase):
    def setUp(self):
        # Create a mock conforming to MusicPlayerProtocol
        self.mock_music_player = MagicMock(spec=MusicPlayerProtocol)
        self.mock_music_player.list_playlists.return_value = [
            "ambient",
            "battle",
            "tavern",
        ]
        self.mock_music_player.volume = 0.5

        # Partially setup a mock state so we don't have to initialize the whole world
        self.mock_state = MagicMock(spec=State)
        self.mock_state.music_manager = self.mock_music_player

        self.command = MusicCommand()

    def test_help_no_subcommand(self):
        lexer = Lexer("")
        result = self.command.execute(lexer, self.mock_state)
        # help() returns None but prints to console
        self.assertIsNone(result)

    def test_play_default_success(self):
        lexer = Lexer("play")
        self.mock_music_player.play.return_value = True

        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Playing music from playlist 'default'.")
        self.mock_music_player.play.assert_called_once_with(None)

    def test_play_default_failure(self):
        lexer = Lexer("play")
        self.mock_music_player.play.return_value = False

        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(
            result,
            "Error: No compatible audio found in the music directory, "
            "and no playlist specified.",
        )
        self.mock_music_player.play.assert_called_once_with(None)

    def test_play_playlist_success(self):
        lexer = Lexer("play ambient")
        self.mock_music_player.play.return_value = True

        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Playing music from playlist 'ambient'.")
        self.mock_music_player.play.assert_called_once_with("ambient")

    def test_play_playlist_failure(self):
        lexer = Lexer("play notfound")
        self.mock_music_player.play.return_value = False

        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(
            result,
            "Error: Playlist 'notfound' not found or contains no compatible audio.",
        )
        self.mock_music_player.play.assert_called_once_with("notfound")

    def test_stop(self):
        lexer = Lexer("stop")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Music stopped.")
        self.mock_music_player.stop.assert_called_once()

    def test_skip(self):
        lexer = Lexer("skip")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Skipped to next track.")
        self.mock_music_player.skip.assert_called_once()

    def test_next(self):
        lexer = Lexer("next")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Skipped to next track.")
        self.mock_music_player.skip.assert_called_once()

    def test_pause(self):
        lexer = Lexer("pause")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Music paused.")
        self.mock_music_player.pause.assert_called_once()

    def test_resume(self):
        lexer = Lexer("resume")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Music resumed.")
        self.mock_music_player.resume.assert_called_once()

    def test_list(self):
        lexer = Lexer("list")
        result = self.command.execute(lexer, self.mock_state)
        expected = "Available Playlists:\n - ambient\n - battle\n - tavern"
        self.assertEqual(result, expected)
        self.mock_music_player.list_playlists.assert_called_once()

    def test_list_empty(self):
        lexer = Lexer("list")
        self.mock_music_player.list_playlists.return_value = []
        result = self.command.execute(lexer, self.mock_state)
        expected = "No playlists found in the music/ directory."
        self.assertEqual(result, expected)

    def test_vol_check(self):
        lexer = Lexer("vol")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Current volume: 50%")
        # the type ignore is because mock properties work but mypy sometimes
        # gets confused

    def test_vol_set_percentage(self):
        lexer = Lexer("vol 75")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Volume set to 75%")
        self.mock_music_player.set_volume.assert_called_once_with(0.75)

    def test_vol_set_float(self):
        # Currently the parser splits on punctuation, but let's test the
        # command directly via mocking Lexer.
        lexer = MagicMock()
        lexer.next.side_effect = ["vol", "0.3", None]
        self.mock_music_player.volume = 0.3
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Volume set to 30%")
        self.mock_music_player.set_volume.assert_called_once_with(0.3)

    def test_vol_set_invalid(self):
        lexer = Lexer("vol loud")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Error: Invalid volume level.")
        self.mock_music_player.set_volume.assert_not_called()

    def test_unknown_subcommand(self):
        lexer = Lexer("dj")
        result = self.command.execute(lexer, self.mock_state)
        self.assertEqual(result, "Error: Unknown music subcommand 'dj'.")

    # --- Completions Tests ---

    def test_completion_empty(self):
        result = self.command.get_completions("", self.mock_state)
        self.assertEqual(len(result), 0)

    def test_completion_base_no_space(self):
        # User implies typing "music", usually handled by completer before delegation,
        # but if delegated they get []
        result = self.command.get_completions("music", self.mock_state)
        self.assertEqual(result, [])

    def test_completion_subcommands(self):
        # User typed "music "
        result = self.command.get_completions("music ", self.mock_state)
        expected = ["play", "stop", "next", "skip", "pause", "resume", "list", "vol"]
        self.assertEqual(result, expected)

    def test_completion_subcommands_partial(self):
        # User typed "music pl"
        result = self.command.get_completions("music p", self.mock_state)
        self.assertEqual(result, ["play", "pause"])

    def test_completion_playlists_space(self):
        # User typed "music play "
        result = self.command.get_completions("music play ", self.mock_state)
        self.assertEqual(result, ["ambient", "battle", "tavern"])

    def test_completion_playlists_partial(self):
        # User typed "music play b"
        result = self.command.get_completions("music play b", self.mock_state)
        self.assertEqual(result, ["battle"])

    def test_completion_beyond(self):
        # User typed "music play battle "
        result = self.command.get_completions("music play battle ", self.mock_state)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
