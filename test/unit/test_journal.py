import unittest
from pathlib import Path

from lib.core.journal import JournalEntry, JournalManager


class TestJournalManager(unittest.TestCase):
    def setUp(self):
        self.gamedir = Path("test_journal_gamedir")
        if not self.gamedir.exists():
            self.gamedir.mkdir()
        self.manager = JournalManager(self.gamedir)

    def tearDown(self):
        if self.gamedir.exists():
            for f in self.gamedir.glob("**/*"):
                if f.is_file():
                    f.unlink()
            for d in self.gamedir.glob("*"):
                if d.is_dir():
                    d.rmdir()
            self.gamedir.rmdir()

    def test_add_and_list_entries(self):
        entry = JournalEntry(title="Test", content="Test Content", timestamp=100.0)
        self.manager.add_entry(entry)
        entries = self.manager.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "Test")
        self.assertEqual(entries[0].content, "Test Content")

    def test_delete_entry(self):
        entry1 = JournalEntry(title="Test1", content="Content1", timestamp=100.0)
        entry2 = JournalEntry(title="Test2", content="Content2", timestamp=200.0)
        self.manager.add_entry(entry1)
        self.manager.add_entry(entry2)

        # Delete by index
        self.assertTrue(self.manager.delete_entry("1"))
        self.assertEqual(len(self.manager.get_entries()), 1)

        # Delete by title
        self.assertTrue(self.manager.delete_entry("Test2"))
        self.assertEqual(len(self.manager.get_entries()), 0)

    def test_load_journal(self):
        journal_file = self.gamedir / "journal.txt"
        journal_file.write_text(
            "Entry 1\n100.0\nContent A\n\n---\n\nEntry 2\ninvalid_time\nContent B"
        )
        manager = JournalManager(self.gamedir)
        entries = manager.get_entries()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].title, "Entry 1")
        self.assertEqual(entries[0].timestamp, 100.0)
        self.assertEqual(entries[1].title, "Entry 2")
        self.assertEqual(entries[1].timestamp, 0.0)
