from rich.console import Console

from lib.core.journey import Journey
from lib.presentation.pretty import PrettyPrinter


class JourneyPrinter(PrettyPrinter):
    """Pretty printer for lists of Journeys."""

    def can_print(self, obj: object) -> bool:
        """Return True if the object is a list of Journey instances."""
        return isinstance(obj, list) and all(isinstance(x, Journey) for x in obj)

    def print(self, obj: object) -> None:
        assert isinstance(obj, list)
        """Print the journey list to stdout."""
        console = Console()
        if not obj:
            console.print("No journeys found.")
            return

        for journey in obj:
            step_str = "infinity" if journey.steps is None else str(journey.steps)
            console.print(
                f"[blue]{journey.id}. {journey.title} ({journey.state}) "
                f"{journey.progress}/{step_str}[/blue]"
            )
