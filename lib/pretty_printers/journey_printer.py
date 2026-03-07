from typing import List

from lib.journey import Journey
from lib.pretty import PrettyPrinter


class JourneyPrinter(PrettyPrinter):
    def can_print(self, obj: any) -> bool:
        return isinstance(obj, list) and all(isinstance(x, Journey) for x in obj)

    def print(self, obj: List[Journey]) -> None:
        if not obj:
            print("No journeys found.")
            return

        for journey in obj:
            step_str = "infinity" if journey.steps is None else str(journey.steps)
            print(
                f"{journey.id}. {journey.title} ({journey.state}) "
                f"{journey.progress}/{step_str}"
            )
