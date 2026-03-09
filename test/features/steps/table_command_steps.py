import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from behave import given, then, when

from lib.core.music import MusicPlayerProtocol
from lib.core.state import StateFactory
from lib.presentation.commands.table_command import TableCommand
from lib.presentation.lexer import Lexer


@given('a game directory with a "tables" folder containing:')
def step_impl_setup_tables(context):
    context.temp_dir = tempfile.mkdtemp()
    context.base_dir = Path(context.temp_dir)
    context.state = StateFactory.create(
        context.base_dir, MagicMock(spec=MusicPlayerProtocol)
    )

    tables_dir = context.base_dir / "tables"
    tables_dir.mkdir()

    for row in context.table:
        filename = row["filename"]
        content = row["content"].replace("\\n", "\n")
        (tables_dir / filename).write_text(content, encoding="utf-8")

    context.state.table_manager.load_tables()
    context.command = TableCommand()


@when('I execute table command "{command_text}"')
def step_impl_type_command(context, command_text):
    lexer = Lexer(command_text)
    lexer.next()  # should be "table"

    # Capture print output
    import sys
    from io import StringIO

    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    context.error = None
    try:
        context.result = context.command.execute(lexer, context.state)
        if context.result is not None:
            print(context.result)
    except Exception as e:
        context.error = e

    sys.stdout = old_stdout
    context.output = mystdout.getvalue()


@then('the command output should include "{text}"')
def step_impl_output_includes(context, text):
    assert text in context.output, f"Expected '{text}' in output, got: {context.output}"


@then("the command output should not be empty")
def step_impl_output_not_empty(context):
    assert context.output.strip() != "", "Expected output to not be empty"


@then("the result should not be added to the journal")
def step_impl_result_not_in_journal(context):
    entries = context.state.journal_manager.get_entries()
    assert len(entries) == 0, "Expected no journal entry to be created."


@then('a SyntaxError should be raised with "{err_msg}"')
def step_impl_syntax_error(context, err_msg):
    assert context.error is not None, "Expected an error but none was raised."
    assert isinstance(context.error, SyntaxError), (
        f"Expected SyntaxError, got {type(context.error)}"
    )
    assert err_msg in str(context.error), (
        f"Expected message '{err_msg}', got '{str(context.error)}'"
    )
