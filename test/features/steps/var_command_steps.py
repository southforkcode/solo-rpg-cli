import tempfile
from pathlib import Path

from behave import given, then, when

from lib.presentation.commands.var_command import VarCommand
from lib.presentation.repl import REPLEnvironment
from lib.core.state import StateFactory


@given("the game is initialized")
def step_impl_game_initialized(context):
    if not hasattr(context, "base_dir"):
        context.temp_dir = tempfile.mkdtemp()
        context.base_dir = Path(context.temp_dir)

    if not hasattr(context, "repl") or context.repl is None:
        state = StateFactory.create(context.base_dir)
        context.repl = REPLEnvironment(context.base_dir, state)
        context.repl.command_registry.register(VarCommand())


@when('I type "{command}"')
@given('I type "{command}"')
def step_impl_type_command(context, command):
    # Execute the command directly by tokenizing it
    import sys
    from io import StringIO

    from lib.presentation.lexer import Lexer

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


@then('I should see "{expected_output}"')
def step_impl_should_see(context, expected_output):
    output = str(context.last_output) if context.last_output is not None else ""
    assert expected_output in output, (
        f"Expected to see '{expected_output}', but saw '{output}'"
    )


@given('a file "{filename}" with the following content:')
def step_impl_file_content(context, filename):
    file_path = context.base_dir / filename
    with open(file_path, "w") as f:
        f.write(context.text)


@given('I load macros from "{filename}"')
def step_impl_load_macros(context, filename):
    context.repl.state.macro_manager.load_macros()
