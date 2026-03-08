import tempfile
import unittest
from pathlib import Path

from lib.core.settings import SettingsManager
from lib.core.table import Table, TableManager


class TestTable(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.tables_dir = self.base_dir / "tables"
        self.tables_dir.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_table_txt_load(self):
        txt_file = self.tables_dir / "names.txt"
        txt_file.write_text("Alice\nBob\nCharlie", encoding="utf-8")

        table = Table("names", txt_file)
        self.assertEqual(len(table.items), 3)
        self.assertIn("Alice", table.items)
        self.assertIn("Charlie", table.items)

        # Test roll
        result = table.roll()
        self.assertIn(result, ["Alice", "Bob", "Charlie"])

    def test_table_csv_load(self):
        csv_file = self.tables_dir / "loot.csv"
        csv_file.write_text("Gold,100\nPotion,50\nSword,10", encoding="utf-8")

        table = Table("loot", csv_file)
        self.assertEqual(len(table.items), 3)
        self.assertEqual(table.items[0], "Gold")
        self.assertEqual(table.items[2], "Sword")

        result = table.roll()
        self.assertIn(result, ["Gold", "Potion", "Sword"])

    def test_table_empty(self):
        empty_file = self.tables_dir / "empty.txt"
        empty_file.write_text("", encoding="utf-8")

        table = Table("empty", empty_file)
        self.assertEqual(len(table.items), 0)
        self.assertIsNone(table.roll())


class TestTableManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.tables_dir = self.base_dir / "tables"
        self.tables_dir.mkdir()

        # Create dummy tables
        (self.tables_dir / "names.txt").write_text("Alice\nBob", encoding="utf-8")
        (self.tables_dir / "loot.csv").write_text("Gold,1\nSilver,2", encoding="utf-8")

        self.manager = TableManager(self.base_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_list_tables(self):
        tables = self.manager.list_tables()
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables, ["loot", "names"])

    def test_roll_valid_table(self):
        result = self.manager.roll("names")
        self.assertIn(result, ["Alice", "Bob"])

    def test_roll_invalid_table(self):
        result = self.manager.roll("nonexistent")
        self.assertIsNone(result)

    def test_no_tables_dir(self):
        empty_dir = tempfile.TemporaryDirectory()
        manager = TableManager(Path(empty_dir.name))

        self.assertEqual(manager.list_tables(), [])
        self.assertIsNone(manager.roll("names"))
        empty_dir.cleanup()

    def test_settings_table_includes(self):
        # Create an external directory for "borrowed" tables
        external_dir = Path(self.temp_dir.name) / "external_data"
        external_dir.mkdir()

        # Borrowed table A
        table_a = external_dir / "borrowed_a.txt"
        table_a.write_text("Row1\nRow2", encoding="utf-8")

        # Borrowed table B (for glob testing)
        glob_dir = external_dir / "glob_tables"
        glob_dir.mkdir()
        (glob_dir / "borrowed_b.txt").write_text("Val1\nVal2", encoding="utf-8")
        (glob_dir / "borrowed_c.txt").write_text("Item1\nItem2", encoding="utf-8")

        # Create settings directory and game.toml
        settings_dir = self.base_dir / "settings"
        settings_dir.mkdir()
        toml_content = """
        [tables]
        external_a = "../external_data/borrowed_a.txt"
        globbed = "../external_data/glob_tables/*.txt"
        """
        (settings_dir / "game.toml").write_text(toml_content, encoding="utf-8")

        # Initialize SettingsManager and TableManager
        settings_manager = SettingsManager(self.base_dir)
        manager = TableManager(self.base_dir, settings_manager=settings_manager)

        # External table directly included
        self.assertIn("external_a", manager.list_tables())
        self.assertIn(manager.roll("external_a"), ["Row1", "Row2"])

        # Tables included via glob
        self.assertIn("borrowed_b", manager.list_tables())
        self.assertIn("borrowed_c", manager.list_tables())
        self.assertIn(manager.roll("borrowed_b"), ["Val1", "Val2"])
