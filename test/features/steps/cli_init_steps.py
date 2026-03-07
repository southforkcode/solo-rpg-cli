import subprocess
import sys
import tempfile
from pathlib import Path

from behave import given, then, when


@given("an existing game directory")
def step_impl_existing_dir(context):
    context.temp_dir = tempfile.mkdtemp()
    context.gamedir = Path(context.temp_dir)
    context.gamedir_path = str(context.gamedir)
    context.should_cleanup = True


@given("a non-existent game directory path")
def step_impl_non_existent_dir(context):
    context.temp_dir = tempfile.mkdtemp()
    context.gamedir = Path(context.temp_dir) / "new_game"
    context.gamedir_path = str(context.gamedir)
    context.should_cleanup = True


@when("I run the CLI with the init flag")
def step_impl_run_cli_with_init(context):
    cmd = [sys.executable, "solo_rpg_cli.py", "--init", context.gamedir_path]
    # We pipe stdin so the repl doesn't block if it gets to that point,
    # though with --init it shouldn't block, it just initializes or errors out.
    # Wait, --init ALSO starts the REPL! 
    # Let's send "exit\n" to stdin so it exits immediately after starting the repl.
    process = subprocess.run(cmd, input="exit\n", text=True, capture_output=True)
    context.returncode = process.returncode
    context.stdout = process.stdout
    context.stderr = process.stderr


@when("I run the CLI without the init flag")
def step_impl_run_cli_without_init(context):
    cmd = [sys.executable, "solo_rpg_cli.py", context.gamedir_path]
    process = subprocess.run(cmd, input="exit\n", text=True, capture_output=True)
    context.returncode = process.returncode
    context.stdout = process.stdout
    context.stderr = process.stderr


@then('the CLI should print "{message}"')
def step_impl_cli_print(context, message):
    output = context.stdout + context.stderr
    assert message in output, f"Expected '{message}' in output, got: {output}"


@then("the CLI should exit with code {code:d}")
def step_impl_exit_code(context, code):
    assert context.returncode == code, (
        f"Expected exit code {code}, got {context.returncode}. "
        f"Output: {context.stdout} {context.stderr}"
    )


@then("the directory should be created")
def step_impl_dir_created(context):
    assert context.gamedir.exists(), (
        f"Directory {context.gamedir_path} was not created"
    )


@then("the CLI should successfully start and exit")
def step_impl_start_and_exit(context):
    assert context.returncode == 0, (
        f"Expected clean exit (code 0), got {context.returncode}. "
        f"Output: {context.stdout} {context.stderr}"
    )
    assert "Bye!" in context.stdout, f"Expected 'Bye!' in output, got {context.stdout}"
