import sys
import tempfile
from io import StringIO
from pathlib import Path

from behave import given, then, when

from lib.presentation.lexer import Lexer
from lib.presentation.repl import REPLEnvironment
from lib.core.state import StateFactory


@given("a new macro testing session")
def step_impl_new_macro_session(context):
    context.temp_dir = tempfile.mkdtemp()
    context.gamedir = Path(context.temp_dir)
    state = StateFactory.create(context.gamedir)
    context.repl = REPLEnvironment(context.gamedir, state)
    context.captured_output = ""


@given('a file "{filename}" exists in the game directory with content:')
def step_impl_file_content(context, filename):
    file_path = context.gamedir / filename
    with open(file_path, "w") as f:
        f.write(context.text)


@when("I reload macros")
def step_impl_reload_macros(context):
    context.repl.state.macro_manager.load_macros()


@when('I run macro "{macro_cmd}"')
def step_impl_run_macro(context, macro_cmd):
    lexer = Lexer(macro_cmd)

    # capture stdout
    old_stdout = sys.stdout
    sys.stdout = my_stdout = StringIO()

    try:
        context.result = context.repl.executor.execute(lexer)
    finally:
        sys.stdout = old_stdout

    context.captured_output = my_stdout.getvalue()


@then('the macro output should contain "{expected}"')
def step_impl_output_contains(context, expected):
    assert expected in context.captured_output, (
        f"Expected '{expected}' in '{context.captured_output}'"
    )


@then('the macro output should contain either "{expected1}" or "{expected2}"')
def step_impl_output_contains_either(context, expected1, expected2):
    assert (
        expected1 in context.captured_output or expected2 in context.captured_output
    ), f"Expected either '{expected1}' or '{expected2}' in '{context.captured_output}'"


@then('the macro output should match regular expression "{pattern}"')
def step_impl_regexp(context, pattern):
    import re

    assert re.search(pattern, context.captured_output) is not None, (
        f"Expected output to match '{pattern}', got:\n{context.captured_output}"
    )
