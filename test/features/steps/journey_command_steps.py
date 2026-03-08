import tempfile
from pathlib import Path

from behave import given, then, when

import lib.presentation.commands.journey_command as journey_command_module
from lib.core.state import StateFactory
from lib.presentation.commands.journey_command import JourneyCommand
from lib.presentation.lexer import Lexer


@given("a new journey session")
def step_impl_new_journey_session(context):
    context.temp_dir = tempfile.mkdtemp()
    context.gamedir = Path(context.temp_dir)
    context.state = StateFactory.create(base_dir=context.gamedir)
    context.state.set("gamedir", context.gamedir)
    context.command = JourneyCommand()
    context.result = None

    context.input_lines = []

    def mock_prompt(*args, **kwargs):
        if not context.input_lines:
            raise EOFError()
        line = context.input_lines.pop(0)
        if line == "<CTRL-C>":
            raise KeyboardInterrupt()
        return line

    context.mock_prompt = mock_prompt


@given('a journey "{title}" with {steps:d} steps')
def step_impl_add_journey(context, title, steps):
    context.state.journey_manager.add_journey(
        title=title, description="Description", difficulty="easy", steps=steps
    )


@when('I type the journey command "{command}"')
def step_impl_type_command(context, command):
    parts = command.split(" ", 1)
    args = parts[1] if len(parts) > 1 else ""
    context.lexer = Lexer(args)

    if context.input_lines:
        original_prompt = journey_command_module.prompt
        journey_command_module.prompt = context.mock_prompt
        context.result = context.command.execute(context.lexer, context.state)
        journey_command_module.prompt = original_prompt
    else:
        # Some commands don't need prompts in tests if input_lines is empty
        # but wait, the "And I enter journey texts" usually comes AFTER
        # "When I type the command". This breaks the chaining.
        # It's better to store the command and execute it when
        # "I enter journey texts" or if no texts, execute immediately.
        context.pending_lexer = Lexer(args)


@when("I enter journey texts:")
def step_impl_enter_journey_text(context):
    context.input_lines = context.text.split("\n")
    original_prompt = journey_command_module.prompt
    journey_command_module.prompt = context.mock_prompt
    context.result = context.command.execute(context.pending_lexer, context.state)
    journey_command_module.prompt = original_prompt


@then("the journey command output should be '{expected}'")
def step_impl_command_output(context, expected):
    assert context.result == expected, f"Expected '{expected}', got '{context.result}'"


@then("the journey list should have {count:d} active journey")
@then("the journey list should have {count:d} active journeys")
def step_impl_journey_list_count(context, count):
    active_journeys = context.state.journey_manager.list_journeys("active")
    assert len(active_journeys) == count, (
        f"Expected {count} active journeys, got {len(active_journeys)}"
    )


@then('the first journal entry should be "{title}"')
def step_impl_journal_first_entry(context, title):
    entries = context.state.journal_manager.get_entries()
    assert len(entries) > 0, "No journal entries found!"
    assert entries[-1].title == title, (
        f"Expected title '{title}', got '{entries[-1].title}'"
    )


@then('the journey "{title}" should be "{status}"')
def step_impl_journey_status(context, title, status):
    journey = context.state.journey_manager.get_journey(title)
    assert journey.state == status, f"Expected {status}, got {journey.state}"
