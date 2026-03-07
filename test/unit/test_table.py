import tempfile
import unittest
from pathlib import Path

from lib.table import Table, TableManager


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
