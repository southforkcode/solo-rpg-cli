from datetime import datetime
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from lib.presentation.commands.summary_command import GameSummary
from lib.presentation.pretty import PrettyPrinter


class SummaryPrinter(PrettyPrinter):
    """Pretty printer for a GameSummary."""

    def can_print(self, obj: object) -> bool:
        """Return True if the object is a GameSummary instance."""
        return isinstance(obj, GameSummary)

    def print(self, obj: object) -> None:
        assert isinstance(obj, GameSummary)
        """Print the summary to stdout using rich."""
        console = Console()

        # Build Active Journeys Table
        if obj.journeys:
            journey_table = Table(
                show_header=True, header_style="bold magenta", expand=True
            )
            journey_table.add_column("ID", style="dim", width=4)
            journey_table.add_column("Journey", style="cyan")
            journey_table.add_column("Difficulty", style="yellow")
            journey_table.add_column("Progress", justify="right", style="green")

            for journey in obj.journeys:
                step_str = "∞" if journey.steps is None else str(journey.steps)
                progress_str = f"{journey.progress}/{step_str}"
                journey_table.add_row(
                    str(journey.id),
                    journey.title,
                    journey.difficulty.capitalize(),
                    progress_str,
                )

            journeys_panel = Panel(
                journey_table,
                title="[bold magenta]Active Journeys[/bold magenta]",
                border_style="magenta",
                padding=(1, 1),
            )
        else:
            journeys_panel = Panel(
                "[italic dim]No active journeys at the moment.[/italic dim]",
                title="[bold magenta]Active Journeys[/bold magenta]",
                border_style="magenta",
            )

        # Build Recent Journal Entries
        if obj.journals:
            entries_text = Text()
            for i, entry in enumerate(obj.journals, start=1):
                dt = datetime.fromtimestamp(entry.timestamp)
                time_str = dt.strftime("%A, %B %d %Y, %I:%M %p")

                # Title
                entries_text.append(f"♦ {entry.title}\n", style="bold green")
                # Timestamp
                entries_text.append(f"  {time_str}\n\n", style="italic dim blue")
                # Content
                # Indent lines slightly
                content_indented = "\n".join(
                    [f"    {line}" for line in entry.content.splitlines()]
                )
                entries_text.append(f"{content_indented}\n", style="white")

                if i < len(obj.journals):
                    entries_text.append("\n" + "─" * 40 + "\n\n", style="dim")

            journal_panel = Panel(
                entries_text,
                title="[bold green]Recent Journal Entries[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        else:
            journal_panel = Panel(
                "[italic dim]The journal is currently empty.[/italic dim]",
                title="[bold green]Recent Journal Entries[/bold green]",
                border_style="green",
            )

        console.print()
        console.print(
            Panel.fit(
                "[bold cyan]Solo RPG Game Summary[/bold cyan]", border_style="cyan"
            )
        )

        console.print(journeys_panel)
        console.print()
        console.print(journal_panel)
        console.print()
