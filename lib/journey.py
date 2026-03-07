import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Journey:
    """A single journey in the game."""

    id: int
    title: str
    description: str
    difficulty: str
    steps: Optional[int]
    progress: int = 0
    state: str = "active"  # active, paused, completed, stopped

    def to_dict(self) -> dict:
        """Convert the dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "steps": self.steps,
            "progress": self.progress,
            "state": self.state,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Journey":
        """Create a Journey from a dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            difficulty=data.get("difficulty", ""),
            steps=data.get("steps", None),
            progress=data.get("progress", 0),
            state=data.get("state", "active"),
        )


class JourneyManager:
    """Manages journeys."""

    def __init__(self, base_dir: Path):
        """Initialize."""
        self.journey_file = base_dir / "journeys.json"
        self._global_index: int = 0
        self._journeys: List[Journey] = []
        self._load()

    def _load(self):
        """Load from JSON file."""
        if self.journey_file.exists():
            with open(self.journey_file, "r") as f:
                data = json.load(f)
                self._global_index = data.get("global_index", 0)
                journeys_data = data.get("journeys", [])
                self._journeys = [Journey.from_dict(jd) for jd in journeys_data]
        else:
            self._global_index = 0
            self._journeys = []

    def _save(self):
        """Save to JSON file."""
        with open(self.journey_file, "w") as f:
            data = {
                "global_index": self._global_index,
                "journeys": [j.to_dict() for j in self._journeys],
            }
            json.dump(data, f, indent=4)

    def add_journey(
        self, title: str, description: str, difficulty: str, steps: Optional[int]
    ) -> Journey:
        """Add a journey."""
        self._global_index += 1
        journey = Journey(
            id=self._global_index,
            title=title,
            description=description,
            difficulty=difficulty,
            steps=steps,
            progress=0,
            state="active",
        )
        self._journeys.append(journey)
        self._save()
        return journey

    def get_journey(self, identifier: str) -> Optional[Journey]:
        """Get by id or title."""
        try:
            jid = int(identifier)
            for j in self._journeys:
                if j.id == jid:
                    return j
        except ValueError:
            pass

        for j in self._journeys:
            if j.title.lower() == identifier.lower():
                return j
        return None

    def list_journeys(self, state_filter: Optional[str] = None) -> List[Journey]:
        """List journeys, optionally filtered by state."""
        if not state_filter:
            return self._journeys.copy()
        return [j for j in self._journeys if j.state == state_filter]

    def remove_journey(self, identifier: str) -> bool:
        """Remove a journey."""
        j = self.get_journey(identifier)
        if j:
            self._journeys.remove(j)
            self._save()
            return True
        return False

    def update_journey(self, journey: Journey):
        """Update an existing journey and save."""
        # Find index and replace, or just save since object is mutated
        for i, j in enumerate(self._journeys):
            if j.id == journey.id:
                self._journeys[i] = journey
                self._save()
                return
