import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from behave import given, then, when

from lib.core.music import MusicPlayerProtocol
from lib.core.state import StateFactory
from lib.presentation.commands.summary_command import SummaryCommand
from lib.presentation.lexer import Lexer


@given("a new summary session")
def step_impl_new_session(context):
    context.temp_dir = tempfile.mkdtemp()
    context.gamedir = Path(context.temp_dir)
    context.state = StateFactory.create(
        base_dir=context.gamedir, music_manager=MagicMock(spec=MusicPlayerProtocol)
    )
    context.state.set("gamedir", context.gamedir)
    context.command = SummaryCommand()
    context.result = None


@when('I type the summary command "{command}"')
def step_impl_type_command(context, command):
    parts = command.split(" ", 1)
    args = parts[1] if len(parts) > 1 else ""
    context.lexer = Lexer(args)
    context.result = context.command.execute(context.lexer, context.state)


@then("the summary should have {journeys:d} active journeys")
@then("the summary should have {journeys:d} active journey")
def step_impl_summary_journeys(context, journeys):
    assert len(context.result.journeys) == journeys, (
        f"Expected {journeys} journeys, got {len(context.result.journeys)}"
    )


@then("the summary should have {journals:d} recent journal entries")
@then("the summary should have {journals:d} recent journal entry")
def step_impl_summary_journals(context, journals):
    assert len(context.result.journals) == journals, (
        f"Expected {journals} journals, got {len(context.result.journals)}"
    )
