import tempfile
from pathlib import Path

from behave import given, then, when

from lib.presentation.lexer import Lexer
from lib.presentation.repl import REPLEnvironment


@given("a new repl session")
def step_impl_new_session(context):
    context.temp_dir = tempfile.mkdtemp()
    context.gamedir = Path(context.temp_dir)
    context.repl = REPLEnvironment(gamedir=context.gamedir)
    context.repl.command_registry.register_directory(Path("lib/presentation/commands"))
    from lib.presentation.command import Command

    context.repl.command_registry.register(
        Command.from_impl(
            "last",
            ["_"],
            "Get the result of the last command",
            context.repl.last_command,
            context.repl.last_help,
        )
    )
    context.repl.pretty_printer_registry.register_directory(Path("lib/presentation/pretty_printers"))
    context.output = ""


@when('I enter the repl command "{command}"')
def step_impl_enter_command(context, command):
    lexer = Lexer(command)

    # Capture standard print output for testing, or just use the return result.
    # From repl.py, result represents the command's return value.
    import io
    import sys

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    result = context.repl.execute(lexer)

    # if it's not None, REPL adds to history and prints it
    # (handled within `repl.run()`, but here we call `execute` directly)
    if result is not None:
        context.repl.history.add(command, result)
        context.repl.print(result)

    captured_stdout = sys.stdout.getvalue()
    sys.stdout = old_stdout

    context.result = result
    context.captured_stdout = captured_stdout


@then('the repl output should contain "{expected}"')
def step_impl_output_contain(context, expected):
    output_str = ""
    if context.result is not None:
        if isinstance(context.result, list):
            output_str = "\n".join(str(item) for item in context.result)
        else:
            output_str = str(context.result)
    output_str += context.captured_stdout

    assert expected in output_str, (
        f"Expected output to contain '{expected}', got '{output_str}'"
    )


@then('the repl output should not contain "{unexpected}"')
def step_impl_output_not_contain(context, unexpected):
    output_str = ""
    if context.result is not None:
        if isinstance(context.result, list):
            output_str = "\n".join(str(item) for item in context.result)
        else:
            output_str = str(context.result)
    output_str += context.captured_stdout

    assert unexpected not in output_str, (
        f"Expected output to not contain '{unexpected}', got '{output_str}'"
    )
