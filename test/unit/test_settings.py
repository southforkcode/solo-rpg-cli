import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lib.core.settings import SettingsManager


class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.settings_dir = self.base_dir / "settings"
        self.settings_dir.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_empty_settings(self):
        manager = SettingsManager(self.base_dir)
        self.assertEqual(manager.settings, {})

    def test_load_toml_settings(self):
        toml_content = """
        [tables]
        names = "../tables/names.txt"
        """
        toml_file = self.settings_dir / "game.toml"
        toml_file.write_text(toml_content)

        manager = SettingsManager(self.base_dir)
        self.assertIn("tables", manager.settings)
        self.assertEqual(manager.get("tables")["names"], "../tables/names.txt")

    def test_load_multiple_toml_files_merging(self):
        file1 = self.settings_dir / "game.toml"
        file1.write_text("[tables]\nnames = 'names.txt'\n")

        file2 = self.settings_dir / "other.toml"
        file2.write_text("[tables]\nplaces = 'places.txt'\n")

        manager = SettingsManager(self.base_dir)
        tables = manager.get("tables")
        self.assertIn("names", tables)
        self.assertIn("places", tables)

    def test_invalid_toml_file(self):
        file1 = self.settings_dir / "bad.toml"
        file1.write_text("[tables\nmissing bracket")

        # Shouldn't crash, just ignore or print error
        manager = SettingsManager(self.base_dir)
        self.assertEqual(manager.settings, {})
