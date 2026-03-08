import unittest
from pathlib import Path
from lib.core.journey import JourneyManager, Journey

class TestJourneyManager(unittest.TestCase):
    def setUp(self):
        self.gamedir = Path("test_journey_gamedir")
        if not self.gamedir.exists():
            self.gamedir.mkdir()
        self.manager = JourneyManager(self.gamedir)

    def tearDown(self):
        if self.gamedir.exists():
            for f in self.gamedir.glob("**/*"):
                if f.is_file(): f.unlink()
            for d in self.gamedir.glob("*"):
                if d.is_dir(): d.rmdir()
            self.gamedir.rmdir()

    def test_add_and_list_journey(self):
        journey = self.manager.add_journey(title="Dragon", description="Kill it", difficulty="hard", steps=5)
        journeys = self.manager.list_journeys()
        self.assertEqual(len(journeys), 1)
        self.assertEqual(journeys[0].title, "Dragon")
        self.assertEqual(journeys[0].state, "active")

    def test_remove_update_and_get(self):
        journey = self.manager.add_journey(title="Goblin", description="Kill it", difficulty="easy", steps=1)
        self.assertIsNotNone(self.manager.get_journey(str(journey.id)))
        
        journey.state = "completed"
        self.assertTrue(self.manager.update_journey(journey))
        self.assertEqual(self.manager.get_journey(str(journey.id)).state, "completed")

        self.assertTrue(self.manager.remove_journey(str(journey.id)))
        self.assertIsNone(self.manager.get_journey(str(journey.id)))
