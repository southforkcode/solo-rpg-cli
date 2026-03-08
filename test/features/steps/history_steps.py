import tempfile
from pathlib import Path

from behave import given, then, when

from lib.core.state import StateFactory
from lib.presentation.lexer import Lexer
from lib.presentation.repl import REPLEnvironment


@given("a new repl session")
def step_impl_new_session(context):
    context.temp_dir = tempfile.mkdtemp()
    context.gamedir = Path(context.temp_dir)
    state = StateFactory.create(context.gamedir)
    context.repl = REPLEnvironment(context.gamedir, state)
    from lib.presentation.commands.journal_command import JournalCommand
    from lib.presentation.commands.journey_command import JourneyCommand
    from lib.presentation.commands.macro_command import MacroCommand
    from lib.presentation.commands.oracle_command import OracleCommand
    from lib.presentation.commands.roll_command import RollCommand
    from lib.presentation.commands.summary_command import SummaryCommand
    from lib.presentation.commands.table_command import TableCommand
    from lib.presentation.commands.var_command import VarCommand

    context.repl.command_registry.register(JournalCommand())
    context.repl.command_registry.register(JourneyCommand())
    context.repl.command_registry.register(MacroCommand())
    context.repl.command_registry.register(OracleCommand())
    context.repl.command_registry.register(RollCommand())
    context.repl.command_registry.register(SummaryCommand())
    context.repl.command_registry.register(TableCommand())
    context.repl.command_registry.register(VarCommand())

    from lib.presentation.repl import _LastCommand

    context.repl.command_registry.register(_LastCommand(context.repl))
    context.repl.pretty_printer_registry.register_directory(
        Path("lib/presentation/pretty_printers")
    )
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

    result = context.repl.executor.execute(lexer)

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
