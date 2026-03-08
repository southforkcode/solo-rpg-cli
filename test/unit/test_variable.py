import unittest
from pathlib import Path

from lib.core.variable import VariableManager


class TestVariableManager(unittest.TestCase):
    def setUp(self):
        self.gamedir = Path("test_var_gamedir")
        if not self.gamedir.exists():
            self.gamedir.mkdir()
        self.manager = VariableManager(self.gamedir)

    def tearDown(self):
        if self.gamedir.exists():
            for f in self.gamedir.glob("**/*"):
                if f.is_file():
                    f.unlink()
            for d in self.gamedir.glob("*"):
                if d.is_dir():
                    d.rmdir()
            self.gamedir.rmdir()

    def test_set_and_get_var(self):
        self.manager.set_var("health", "100")
        self.assertEqual(self.manager.get_var("health"), "100")
        self.assertEqual(self.manager.get_var("mana", "50"), "50")
        all_vars = self.manager.get_all()
        self.assertIn("health", all_vars)
        self.manager.delete_var("health")
        self.assertIsNone(self.manager.get_var("health"))
