from datetime import datetime
from typing import Any

import prompt_toolkit
from rich.console import Console

from lib.core.journal import JournalEntry
from lib.core.journey import Journey
from lib.core.state import State
from lib.presentation.command import Command
from lib.presentation.lexer import Lexer


def prompt(*args: Any, **kwargs: Any) -> str:
    """Wrapper around prompt_toolkit.prompt for easy mocking in tests."""
    return prompt_toolkit.prompt(*args, **kwargs)


class JourneyCommand(Command):
    """The command for managing journeys."""

    def __init__(self):
        """Initialize the JourneyCommand."""
        super().__init__()
        self.command = "journey"
        self.aliases = []
        self.description = "Manage journeys"

    def get_completions(self, text_before_cursor: str, state: State) -> list[str]:
        """Return a list of autocomplete suggestions."""
        words = text_before_cursor.split()
        if not words:
            return []

        is_new_word = text_before_cursor.endswith(" ")
        verbs = [
            "start",
            "list",
            "progress",
            "pause",
            "resume",
            "complete",
            "stop",
            "remove",
            "rm",
        ]

        if len(words) == 1 and not is_new_word:
            return []

        if len(words) == 1 and is_new_word:
            return verbs

        if len(words) == 2 and not is_new_word:
            prefix = words[1].lower()
            return [v for v in verbs if v.startswith(prefix)]

        verb = words[1].lower()
        if verb in ["progress", "pause", "resume", "complete", "stop", "remove", "rm"]:
            if verb in ["progress", "pause", "complete", "stop"]:
                journeys = state.journey_manager.list_journeys("active")
            elif verb == "resume":
                journeys = state.journey_manager.list_journeys("paused")
            else:
                journeys = state.journey_manager.list_journeys()

            titles = [j.title for j in journeys] + [str(j.id) for j in journeys]
            titles = [f'"{t}"' if " " in t else t for t in titles]

            if len(words) == 2 and is_new_word:
                return titles

            if len(words) == 3 and not is_new_word:
                prefix = words[2].lower()
                clean_prefix = prefix.strip("\"'")
                return [
                    t for t in titles if t.strip("\"'").lower().startswith(clean_prefix)
                ]

        return []

    def execute(self, lexer: Lexer, state: State) -> object:
        """Execute the journey command by routing to the appropriate subcommand."""
        subcommand = lexer.next()

        if not subcommand:
            self.help()
            return None

        if subcommand == "start":
            return self.start_subcommand(lexer, state)
        elif subcommand == "list":
            return self.list_subcommand(lexer, state)
        elif subcommand == "progress":
            return self.progress_subcommand(lexer, state)
        elif subcommand == "pause":
            return self.state_subcommand(lexer, state, "paused", "paused.")
        elif subcommand == "resume":
            return self.state_subcommand(lexer, state, "active", "now active.")
        elif subcommand == "complete":
            return self.state_subcommand(lexer, state, "completed", "was completed!")
        elif subcommand == "stop":
            return self.state_subcommand(
                lexer, state, "stopped", "stopped indefinitely."
            )
        elif subcommand in ["remove", "rm"]:
            return self.remove_subcommand(lexer, state)
        else:
            return f"Error: Unknown journey subcommand '{subcommand}'"

    def _get_title(self, lexer: Lexer) -> str:
        """Parse a multi-word or quoted title from the Lexer."""
        title_parts = []
        while True:
            part = lexer.next()
            if part is None:
                break
            title_parts.append(part)
        return " ".join(title_parts).strip("\"'")

    def start_subcommand(self, lexer: Lexer, state: State) -> object:
        """Start a new journey interactively."""
        title = self._get_title(lexer)
        if not title:
            return "Error: Please provide a journey title."

        print(
            "journey> (Type '...' on a new line or "
            "press Ctrl-D to save, Ctrl-C to cancel)"
        )
        desc_lines = []
        try:
            while True:
                line = prompt("journey>")
                if line.strip() == "...":
                    break
                desc_lines.append(line)
        except EOFError:
            pass
        except KeyboardInterrupt:
            return "Journey cancelled."

        description = "\n".join(desc_lines)

        try:
            difficulty = prompt("Difficulty? ")
            steps_str = prompt("Steps: ")
        except (EOFError, KeyboardInterrupt):
            return "Journey cancelled."

        steps = None
        if steps_str.strip():
            try:
                steps = int(steps_str)
            except ValueError:
                return "Error: Steps must be an integer."

        state.journey_manager.add_journey(title, description, difficulty, steps)

        content = description
        if not content:
            content = f"Difficulty: {difficulty}"
            if steps:
                content += f" Steps: {steps}"

        entry = JournalEntry(
            title=f"Started Journey: {title}",
            content=content,
            timestamp=datetime.now().timestamp(),
        )
        state.journal_manager.add_entry(entry)

        return f'Journey "{title}" started.'

    def list_subcommand(self, lexer: Lexer, state: State) -> object:
        """List active, paused, completed, or all journeys."""
        flag = lexer.next()
        if not flag:
            flag = "-active"

        state_filter = None
        if flag == "-active":
            state_filter = "active"
            print("Active journeys are:")
        elif flag == "-paused":
            state_filter = "paused"
            print("Paused journeys are:")
        elif flag == "-completed":
            state_filter = "completed"
            print("Completed journeys are:")
        elif flag == "-all":
            state_filter = None
            print("All journeys:")

        return state.journey_manager.list_journeys(state_filter)

    def _get_journey(self, identifier: str, state: State) -> Journey | None:
        """Retrieve a journey by title or ID from the manager."""
        return state.journey_manager.get_journey(identifier)

    def progress_subcommand(self, lexer: Lexer, state: State) -> object:
        """Progress a journey toward completion."""
        identifier = self._get_title(lexer)
        if not identifier:
            return "Error: Please provide a journey identifier."

        journey = self._get_journey(identifier, state)
        if not journey:
            return f'Error: Journey "{identifier}" not found.'

        if journey.state != "active":
            return f"Error: Journey is not active ({journey.state})."

        old_progress = journey.progress
        step_str = "infinity" if journey.steps is None else str(journey.steps)
        journey.progress += 1

        state.journey_manager.update_journey(journey)

        print(
            f'Journey "{journey.title}" ({journey.state}) progressed '
            f"from {old_progress}/{step_str} to {journey.progress}/{step_str}."
        )

        try:
            comment = prompt("Comment? ")
        except (EOFError, KeyboardInterrupt):
            comment = ""

        completed = False
        if journey.steps is not None and journey.progress >= journey.steps:
            journey.state = "completed"
            state.journey_manager.update_journey(journey)
            print(f'Journey "{journey.title}" was completed!')
            completed = True

        entry_title = f"Journey Progressed: {journey.title}"
        if completed:
            entry_title += " (Completed)"

        entry = JournalEntry(
            title=entry_title, content=comment, timestamp=datetime.now().timestamp()
        )
        state.journal_manager.add_entry(entry)

        return None

    def state_subcommand(
        self, lexer: Lexer, state: State, new_state: str, action_str: str
    ) -> object:
        """Transition a journey to a semantic new state (pause, complete, etc.)."""
        identifier = self._get_title(lexer)
        if not identifier:
            return "Error: Please provide a journey identifier."

        journey = self._get_journey(identifier, state)
        if not journey:
            return f'Error: Journey "{identifier}" not found.'

        try:
            comment = prompt("Comment? ")
        except (EOFError, KeyboardInterrupt):
            comment = ""

        journey.state = new_state
        state.journey_manager.update_journey(journey)

        step_str = "infinity" if journey.steps is None else str(journey.steps)

        print(f'Journey "{journey.title}" ({journey.progress}/{step_str}) {action_str}')

        entry = JournalEntry(
            title=f"Journey {new_state.capitalize()}: {journey.title}",
            content=comment,
            timestamp=datetime.now().timestamp(),
        )
        state.journal_manager.add_entry(entry)

        return None

    def remove_subcommand(self, lexer: Lexer, state: State) -> object:
        """Permanently remove a journey."""
        identifier = self._get_title(lexer)
        if not identifier:
            return "Error: Please provide a journey identifier."

        journey = self._get_journey(identifier, state)
        if not journey:
            return f'Error: Journey "{identifier}" not found.'

        step_str = "infinity" if journey.steps is None else str(journey.steps)

        console = state.get("console")
        if console:
            prompt_str = (
                f'Remove journey "{journey.title}" ({journey.progress}/{step_str})?'
            )
            if not console.confirm(prompt_str):
                return "Cancelled."
        else:
            # Fallback if console is not available in state for some reason
            try:
                ans = prompt(
                    f'Remove journey "{journey.title}" '
                    f"({journey.progress}/{step_str}) Y/N? "
                )
            except (EOFError, KeyboardInterrupt):
                return "Cancelled."
            if ans.lower() != "y":
                return "Cancelled."

        state.journey_manager.remove_journey(str(journey.id))
        return f'Journey "{journey.title}" removed.'

    def help(self):
        """Print help information for the journey command."""
        console = Console()
        console.print(
            "[bold cyan]journey[/bold cyan] [bold]start[/bold] "
            "[italic]<title>[/italic] - Start a new journey"
        )
        console.print(
            "  [bold cyan]journey[/bold cyan] [bold]list[/bold] "
            "\\[[bold]-active[/bold]|[bold]-paused[/bold]|[bold]-completed[/bold]|"
            "[bold]-all[/bold]] - List journeys"
        )
        console.print(
            "  [bold cyan]journey[/bold cyan] [bold]progress[/bold] "
            "[italic]<identifier>[/italic] - Progress a journey"
        )
        console.print(
            "  [bold cyan]journey[/bold cyan] [bold]pause[/bold] "
            "[italic]<identifier>[/italic] - Pause a journey"
        )
        console.print(
            "  [bold cyan]journey[/bold cyan] [bold]resume[/bold] "
            "[italic]<identifier>[/italic] - Resume a paused journey"
        )
        console.print(
            "  [bold cyan]journey[/bold cyan] [bold]complete[/bold] "
            "[italic]<identifier>[/italic] - Complete a journey"
        )
        console.print(
            "  [bold cyan]journey[/bold cyan] [bold]stop[/bold] "
            "[italic]<identifier>[/italic] - Stop a journey indefinitely"
        )
        console.print(
            "  [bold cyan]journey[/bold cyan] [bold]remove[/bold] "
            "[italic]<identifier>[/italic] - Remove a journey"
        )
