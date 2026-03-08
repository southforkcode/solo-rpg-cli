from unittest.mock import MagicMock

from prompt_toolkit.document import Document

from lib.core.state import State
from lib.presentation.command import Command, CommandRegistry
from lib.presentation.completer import REPLCompleter


class DummyCommand(Command):
    def __init__(self, command, completions=None):
        super().__init__()
        self.command = command
        self.aliases = []
        self._mock_completions = completions or []

    def execute(self, lexer, state):
        pass

    def help(self):
        pass

    def get_completions(self, text_before_cursor, state):
        return self._mock_completions


def test_repl_completer_empty():
    registry = CommandRegistry()
    registry.register(DummyCommand("journey"))

    state = MagicMock(spec=State)
    state.macro_manager = None

    completer = REPLCompleter(registry, state)
    doc = Document("", cursor_position=0)
    completions = list(completer.get_completions(doc, None))

    assert len(completions) == 1
    assert completions[0].text == "journey"


def test_repl_completer_command_prefix():
    registry = CommandRegistry()
    registry.register(DummyCommand("journey"))
    registry.register(DummyCommand("journal"))

    state = MagicMock(spec=State)
    state.macro_manager = None

    completer = REPLCompleter(registry, state)
    doc = Document("jour", cursor_position=4)
    completions = list(completer.get_completions(doc, None))

    texts = [c.text for c in completions]
    assert "journey" in texts
    assert "journal" in texts
    assert len(texts) == 2


def test_repl_completer_subcommand():
    registry = CommandRegistry()
    cmd = DummyCommand("journey", completions=["start", "stop", "status"])
    registry.register(cmd)

    state = MagicMock(spec=State)

    completer = REPLCompleter(registry, state)
    doc = Document("journey st", cursor_position=10)
    completions = list(completer.get_completions(doc, None))

    texts = [c.text for c in completions]
    assert len(texts) == 3
    assert "start" in texts
    assert "stop" in texts
    assert "status" in texts
