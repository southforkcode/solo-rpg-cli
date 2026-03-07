from pathlib import Path

from behave import then, when

from lib.commands.oracle_command import OracleCommand
from lib.lexer import Lexer
from lib.state import State


@when('I execute the oracle command with \'{args}\'')
def step_impl_execute_oracle_single_quotes(context, args):
    lexer = Lexer(args)
    state = State(base_dir=Path("/tmp/dummy"))
    command = OracleCommand()
    context.error = None
    context.result = None
    try:
        context.result = command.execute(lexer, state)
    except Exception as e:
        context.error = e


@when('I execute the oracle command with "{args}"')
def step_impl_execute_oracle(context, args):
    # Depending on how the string is parsed in Behave, 
    # the steps parser might strip outer quotes from the step definition string.
    lexer = Lexer(args)
    state = State(base_dir=Path("/tmp/dummy"))
    command = OracleCommand()
    context.error = None
    context.result = None
    try:
        context.result = command.execute(lexer, state)
    except Exception as e:
        context.error = e


@then("the oracle command returns a result")
def step_impl_returns_result_oracle(context):
    assert context.error is None, f"Expected no error but got: {context.error}"
    assert context.result is not None, "Expected a result, but got None"


@then('the oracle result starts with "{prefix}"')
def step_impl_starts_with(context, prefix):
    assert context.result.startswith(prefix), f"Expected result to start with '{prefix}', got '{context.result}'"


@then('the oracle result contains the question "{question}"')
def step_impl_contains_question(context, question):
    assert question in context.result, f"Expected result to contain '{question}', got '{context.result}'"


@then("the oracle command raises a SyntaxError")
def step_impl_raises_syntax_error_oracle(context):
    assert context.error is not None, "Expected an error but got None"
    assert isinstance(context.error, SyntaxError), (
        f"Expected SyntaxError, got {type(context.error)}"
    )
