from dataclasses import dataclass
from typing import Any, List

from lib.command import Command
from lib.journal import JournalEntry
from lib.journey import Journey
from lib.lexer import Lexer
from lib.state import State


@dataclass
class GameSummary:
    journeys: List[Journey]
    journals: List[JournalEntry]


class SummaryCommand(Command):
    """The command for summarizing the current state of the game."""

    def __init__(self):
        super().__init__()
        self.command = "summary"
        self.aliases = ["s"]
        self.description = "Summarize the current state of the game"

    def execute(self, lexer: Lexer, state: State) -> Any:
        # We don't have subcommands, but we should consume remaining tokens if any, or just ignore.
        _ = lexer.next() # optional subcommand or garbage
        
        journals = state.journal_manager.get_entries(5)
        journeys = state.journey_manager.list_journeys("active")
        return GameSummary(journeys=journeys, journals=journals)

    def help(self):
        print("summary|s - Summarize the current state of the game (last 5 journal entries and active journeys)")
