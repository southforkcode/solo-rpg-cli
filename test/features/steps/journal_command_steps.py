import tempfile
from pathlib import Path

from behave import given, then, when

import lib.presentation.commands.journal_command as journal_command_module
from lib.core.journal import JournalEntry
from lib.core.state import State
from lib.presentation.commands.journal_command import JournalCommand
from lib.presentation.lexer import Lexer


@given("a new standard session")
def step_impl_new_session(context):
    context.temp_dir = tempfile.mkdtemp()
    context.gamedir = Path(context.temp_dir)
    context.state = State(base_dir=context.gamedir)
    context.state.set("gamedir", context.gamedir)
    context.command = JournalCommand()
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


@given('a journal entry with title "{title}" and content "{content}"')
def step_impl_add_journal_entry(context, title, content):
    context.state.journal_manager.add_entry(
        JournalEntry(title=title, content=content, timestamp=12345.0)
    )


@when('I type the command "{command}"')
def step_impl_type_command(context, command):
    # Strip the leading command (journal or j)
    parts = command.split(" ", 1)
    args = parts[1] if len(parts) > 1 else ""
    # In tests, we need the subcommand as the first token
    context.lexer = Lexer(args)

    # We execute immediately if it's not 'add'
    # Actually wait, 'add' needs mocked prompt, 'list' and 'delete' don't.
    # Let's just execute standard stuff here unless it's overriden
    if "list" in args or "delete" in args or "del" in args:
        context.result = context.command.execute(context.lexer, context.state)


@when("I enter journal text:")
def step_impl_enter_journal_text(context):
    context.input_lines = context.text.split("\n")

    original_prompt = journal_command_module.prompt
    journal_command_module.prompt = context.mock_prompt

    context.result = context.command.execute(context.lexer, context.state)

    journal_command_module.prompt = original_prompt


@when("I enter journal text and press ctrl-c:")
def step_impl_enter_journal_text_ctrlc(context):
    context.input_lines = context.text.split("\n")
    context.input_lines.append("<CTRL-C>")

    original_prompt = journal_command_module.prompt
    journal_command_module.prompt = context.mock_prompt

    context.result = context.command.execute(context.lexer, context.state)

    journal_command_module.prompt = original_prompt


@then('the command output should be "{expected}"')
def step_impl_command_output(context, expected):
    assert context.result == expected, f"Expected '{expected}', got '{context.result}'"


@then("the journal should have {count:d} entry")
@then("the journal should have {count:d} entries")
def step_impl_journal_count(context, count):
    entries = context.state.journal_manager.get_entries()
    assert len(entries) == count, f"Expected {count} entries, got {len(entries)}"


@then('the first journal entry should have title "{title}"')
def step_impl_journal_title(context, title):
    entries = context.state.journal_manager.get_entries()
    assert entries[0].title == title, (
        f"Expected title '{title}', got '{entries[0].title}'"
    )


@then('the first journal entry title should start with "{prefix}"')
def step_impl_journal_title_prefix(context, prefix):
    entries = context.state.journal_manager.get_entries()
    assert entries[0].title.startswith(prefix), (
        f"Expected title to start with '{prefix}', got '{entries[0].title}'"
    )


@then('the first journal entry should contain "{content}"')
def step_impl_journal_content(context, content):
    entries = context.state.journal_manager.get_entries()
    assert content in entries[0].content, (
        f"Expected content to contain '{content}', got '{entries[0].content}'"
    )


@then('the output should contain "{content}"')
def step_impl_output_contain(context, content):
    if isinstance(context.result, list):
        found = any(
            content in entry.title or content in entry.content
            for entry in context.result
        )
        assert found, f"Expected output to contain '{content}'"
    elif isinstance(context.result, str):
        assert content in context.result, (
            f"Expected output to contain '{content}', got '{context.result}'"
        )
    else:
        raise AssertionError(f"Unexpected result type: {type(context.result)}")
