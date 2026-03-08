from pathlib import Path

from behave import then, when

from lib.core.dice_roller import DiceRerollType
from lib.core.state import StateFactory
from lib.presentation.commands.roll_command import RollCommand
from lib.presentation.lexer import Lexer


@when('I execute the roll command with "{args}"')
def step_impl_execute_roll(context, args):
    lexer = Lexer(args)
    state = StateFactory.create(base_dir=Path("/tmp/dummy"))
    command = RollCommand()
    context.error = None
    context.result = None
    try:
        context.result = command.execute(lexer, state)
    except Exception as e:
        context.error = e


@when("I execute the roll command without arguments")
def step_impl_execute_roll_no_args(context):
    step_impl_execute_roll(context, "")


@then("the roll command returns a result")
def step_impl_returns_result(context):
    assert context.error is None, f"Expected no error but got: {context.error}"
    assert context.result is not None, "Expected a result, but got None"


@then("the roll result should be between {min_val:d} and {max_val:d}")
def step_impl_result_range(context, min_val, max_val):
    result = context.result.total
    assert min_val <= result <= max_val, (
        f"Result {result} is not between {min_val} and {max_val}"
    )


@then("exactly {expected_rolls:d} die was rolled")
@then("exactly {expected_rolls:d} dice were rolled")
def step_impl_exact_dice(context, expected_rolls):
    actual_rolls = len(context.result.results)
    assert actual_rolls == expected_rolls, (
        f"Expected {expected_rolls} rolls, got {actual_rolls}"
    )


@then("the roll has advantage")
def step_impl_has_advantage(context):
    assert context.result.dice_roll.reroll_type == DiceRerollType.ADVANTAGE, (
        f"Expected advantage, got {context.result.dice_roll.reroll_type}"
    )


@then("the roll has disadvantage")
def step_impl_has_disadvantage(context):
    assert context.result.dice_roll.reroll_type == DiceRerollType.DISADVANTAGE, (
        f"Expected disadvantage, got {context.result.dice_roll.reroll_type}"
    )


@then("the roll command raises a SyntaxError")
def step_impl_raises_syntax_error(context):
    assert context.error is not None, "Expected an error but got None"
    assert isinstance(context.error, SyntaxError), (
        f"Expected SyntaxError, got {type(context.error)}"
    )
