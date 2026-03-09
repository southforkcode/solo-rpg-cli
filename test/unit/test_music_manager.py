import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from lib.core.music import MusicManager


class TestMusicManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for tests
        self.patcher_gamedir = patch("pathlib.Path.mkdir")
        self.mock_mkdir = self.patcher_gamedir.start()
        
        self.gamedir = Path("/mock/gamedir")
        
        # Patch pygame
        self.patcher_pygame = patch("lib.core.music.pygame")
        self.mock_pygame = self.patcher_pygame.start()
        
        # Prevent threading in tests
        self.patcher_thread = patch("lib.core.music.threading.Thread")
        self.mock_thread = self.patcher_thread.start()

        self.manager = MusicManager(self.gamedir)

    def tearDown(self):
        self.patcher_gamedir.stop()
        self.patcher_pygame.stop()
        self.patcher_thread.stop()

    def test_init(self):
        self.assertEqual(self.manager.gamedir, self.gamedir)
        self.assertEqual(self.manager.music_dir, self.gamedir / "music")
        self.mock_pygame.mixer.init.assert_called_once()
        self.mock_thread.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.glob")
    def test_play_success(self, mock_glob, mock_is_file, mock_is_dir, mock_exists):
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_is_file.return_value = True
        
        mock_file1 = Path("/mock/gamedir/music/ambient/song1.mp3")
        mock_file2 = Path("/mock/gamedir/music/ambient/song2.mp3")
        
        # glob is called 3 times ("*.mp3", "*.ogg", "*.wav")
        mock_glob.side_effect = [[mock_file1, mock_file2], [], []]

        result = self.manager.play("ambient")

        self.assertTrue(result)
        self.assertEqual(self.manager.current_playlist, [mock_file1, mock_file2])
        self.assertEqual(self.manager.current_track_index, 0)
        self.assertTrue(self.manager.is_playing)
        self.mock_pygame.mixer.music.load.assert_called_once_with(str(mock_file1))
        self.mock_pygame.mixer.music.set_volume.assert_called_once_with(1.0)
        self.mock_pygame.mixer.music.play.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_dir")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.glob")
    def test_play_default(self, mock_glob, mock_is_file, mock_is_dir, mock_exists):
        # Test playing directly from music/
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_is_file.return_value = True
        
        mock_file1 = Path("/mock/gamedir/music/song1.mp3")
        
        # glob is called 3 times ("*.mp3", "*.ogg", "*.wav")
        mock_glob.side_effect = [[mock_file1], [], []]

        result = self.manager.play()

        self.assertTrue(result)
        self.assertEqual(self.manager.current_playlist, [mock_file1])
        self.mock_pygame.mixer.music.load.assert_called_once_with(str(mock_file1))
        self.mock_pygame.mixer.music.play.assert_called_once()

    @patch("pathlib.Path.exists")
    def test_play_playlist_not_found(self, mock_exists):
        mock_exists.return_value = False
        result = self.manager.play("nonexistent")
        self.assertFalse(result)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("lib.core.music.tomllib.load")
    def test_play_from_toml(self, mock_toml_load, mock_open_file, mock_is_file, mock_exists):
        # Setup mocking to pretend music.toml exists and has paths
        mock_exists.return_value = True
        mock_is_file.return_value = True
        
        mock_toml_load.return_value = {
            "music": {
                "playlists": {
                    "ambient": {
                        "tracks": ["file1.mp3", "file2.ogg"]
                    }
                }
            }
        }
        
        result = self.manager.play("ambient")
        
        self.assertTrue(result)
        self.assertEqual(len(self.manager.current_playlist), 2)
        self.assertEqual(self.manager.current_playlist[0].name, "file1.mp3")
        self.assertEqual(self.manager.current_playlist[1].name, "file2.ogg")
        self.mock_pygame.mixer.music.load.assert_called_once_with(str(self.gamedir / "music" / "file1.mp3"))
        self.mock_pygame.mixer.music.play.assert_called_once()

    def test_stop(self):
        self.manager.is_playing = True
        self.manager.stop()
        self.mock_pygame.mixer.music.stop.assert_called_once()
        self.assertFalse(self.manager.is_playing)

    def test_pause_resume(self):
        self.manager.is_playing = True
        
        self.manager.pause()
        self.assertTrue(self.manager.is_paused)
        self.mock_pygame.mixer.music.pause.assert_called_once()
        
        self.manager.resume()
        self.assertFalse(self.manager.is_paused)
        self.mock_pygame.mixer.music.unpause.assert_called_once()
        
    def test_set_volume(self):
        self.manager.set_volume(0.5)
        self.assertEqual(self.manager.volume, 0.5)
        self.mock_pygame.mixer.music.set_volume.assert_called_with(0.5)
        
        # Test out of bounds
        self.manager.set_volume(1.5)
        self.assertEqual(self.manager.volume, 1.0)
        
        self.manager.set_volume(-0.5)
        self.assertEqual(self.manager.volume, 0.0)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.iterdir")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("lib.core.music.tomllib.load")
    def test_list_playlists_combined(self, mock_toml_load, mock_open_file, mock_iterdir, mock_is_file, mock_exists):
        # music.toml exists and physical directory fallback exists
        mock_exists.return_value = True
        mock_is_file.return_value = True
        
        mock_toml_load.return_value = {
            "music": {
                "playlists": {
                    "toml_playlist": {"tracks": []},
                    "conflict_playlist": {"tracks": []}
                }
            }
        }
        
        mock_dir1 = MagicMock()
        mock_dir1.is_dir.return_value = True
        mock_dir1.name = "ambient"
        
        mock_dir2 = MagicMock()
        mock_dir2.is_dir.return_value = True
        mock_dir2.name = "conflict_playlist"
        
        mock_file = MagicMock()
        mock_file.is_dir.return_value = False
        mock_file.name = "not_a_playlist.txt"
        
        mock_iterdir.return_value = [mock_dir2, mock_file, mock_dir1]
        
        result = self.manager.list_playlists()
        # Should combine physical dirs + toml ones, deduplicated and sorted
        self.assertEqual(result, ["ambient", "conflict_playlist", "toml_playlist"])

if __name__ == "__main__":
    unittest.main()
