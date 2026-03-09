import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from behave import given, then, when

from lib.core.music import MusicPlayerProtocol
from lib.core.state import StateFactory
from lib.presentation.commands.var_command import VarCommand
from lib.presentation.repl import REPLEnvironment


@given("the game is initialized")
def step_impl_game_initialized(context):
    if not hasattr(context, "base_dir"):
        context.temp_dir = tempfile.mkdtemp()
        context.base_dir = Path(context.temp_dir)

    if not hasattr(context, "repl") or context.repl is None:
        state = StateFactory.create(
            context.base_dir, MagicMock(spec=MusicPlayerProtocol)
        )
        from lib.presentation.console import MockConsole

        context.console = MockConsole(inputs=[])
        context.repl = REPLEnvironment(context.base_dir, state, context.console)
        context.repl.command_registry.register(VarCommand())


@when('I type "{command}"')
@given('I type "{command}"')
def step_impl_type_command(context, command):
    # Execute the command directly by tokenizing it
    import sys
    from io import StringIO

    from lib.presentation.lexer import Lexer

    # Test hack: auto-confirm deletions
    if hasattr(context, "console"):
        parts = command.split()
        if len(parts) >= 2 and parts[0] == "var" and parts[1] == "delete":
            context.console.inputs.append("y")

    lexer = Lexer(command)

    old_stdout = sys.stdout
    sys.stdout = my_stdout = StringIO()
    try:
        context.last_output = context.repl.executor.execute(lexer)
    except Exception as e:
        context.last_output = str(e)
    finally:
        sys.stdout = old_stdout

    captured = my_stdout.getvalue().strip()
    if captured:
        if context.last_output is None:
            context.last_output = captured
        else:
            context.last_output = str(context.last_output) + "\n" + captured

    # Bridge for compatibility with journal_command_steps.py
    context.result = context.last_output


@then('I should see "{expected_output}"')
def step_impl_should_see(context, expected_output):
    output = str(context.last_output) if context.last_output is not None else ""
    assert expected_output in output, (
        f"Expected to see '{expected_output}', but saw '{output}'"
    )


@given('a file "{filename}" with the following content:')
def step_impl_file_content(context, filename):
    file_path = context.base_dir / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with (
        open(file_path, "wb")
        if filename.endswith(".toml")
        else open(file_path, "w") as f
    ):
        if filename.endswith(".toml"):
            f.write(context.text.encode("utf-8"))
        else:
            f.write(context.text)


@given('I load macros from "{filename}"')
def step_impl_load_macros(context, filename):
    context.repl.state.macro_manager.load_macros()
