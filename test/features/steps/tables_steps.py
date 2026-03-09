import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from behave import given, then, when

from lib.core.music import MusicPlayerProtocol
from lib.core.state import StateFactory
from lib.presentation.commands.table_command import TableCommand
from lib.presentation.lexer import Lexer


@given("a new campaign")
def step_impl_new_campaign(context):
    context.temp_dir = tempfile.mkdtemp()
    context.gamedir = Path(context.temp_dir)
    context.state = StateFactory.create(
        context.gamedir, MagicMock(spec=MusicPlayerProtocol)
    )
    context.command = TableCommand()


@given(
    'a custom table named "{table_name}" with items "{items_csv}" '
    'exists in "{directory_name}" directory'
)
def step_impl_create_external_table(context, table_name, items_csv, directory_name):
    # Create the external directory within the temp root (alongside gamedir)
    root_dir = context.gamedir.parent
    external_dir = root_dir / directory_name
    external_dir.mkdir(exist_ok=True)

    file_path = external_dir / f"{table_name}.csv"

    # Write items to CSV format
    lines = items_csv.split(",")
    content = "\\n".join(f"{item},1" for item in lines)
    file_path.write_text(content, encoding="utf-8")


@given('a setting file configuring table "{alias}" points to the "{table_name}" table')
def step_impl_configure_table_settings(context, alias, table_name):
    settings_dir = context.gamedir / "settings"
    settings_dir.mkdir(exist_ok=True)

    settings_file = settings_dir / "game.toml"

    toml_content = f"""
    [tables]
    {alias} = "../../borrowed/{table_name}.csv"
    """
    settings_file.write_text(toml_content)

    # Reload settings/tables in the active state
    context.state.settings_manager.load_settings()
    context.state.table_manager.load_tables()


@when('I enter a command "{command_text}"')
def step_impl_enter_command(context, command_text):
    lexer = Lexer(command_text)
    lexer.next()  # Consume initial token

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

    # Exposing the console wrapper compatibility since we mock stdout directly
    if not hasattr(context, "console"):

        class MockConsole:
            outputs = [context.output]

        context.console = MockConsole()


@then('the table output should contain "{expected1}" or "{expected2}"')
def step_impl_output_contains_either(context, expected1, expected2):
    output = context.console.outputs[-1]
    assert expected1 in output or expected2 in output, (
        f"Expected '{expected1}' or '{expected2}', but got: {output}"
    )
