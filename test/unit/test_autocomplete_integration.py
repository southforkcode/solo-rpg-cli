from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from prompt_toolkit.input.defaults import create_pipe_input

from lib.core.music import MusicPlayerProtocol
from lib.core.state import StateFactory
from lib.presentation.repl import REPLEnvironment


def test_autocomplete_integration():
    with TemporaryDirectory() as tmp_dir:
        gamedir = Path(tmp_dir)
        state = StateFactory.create(gamedir, MagicMock(spec=MusicPlayerProtocol))
        repl = REPLEnvironment(gamedir, state)

        from lib.presentation.commands.journey_command import JourneyCommand

        repl.command_registry.register(JourneyCommand())

        assert repl.console.completer is repl.completer

        # Verify the PromptSession will use the completer
        with create_pipe_input():
            session = repl.console.session
            assert session.completer is repl.completer

            # Verify that when the REPL completes the Document,
            # it gets results down the chain.
            from prompt_toolkit.document import Document

            doc = Document("jour", cursor_position=4)
            completions = list(session.completer.get_completions(doc, None))

            assert len(completions) > 0
            assert any(c.text == "journey" for c in completions)
