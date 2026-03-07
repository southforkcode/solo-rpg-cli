from behave import given, then, when

from lib.core.dice_roller import DiceRerollType, DiceRoller


@given("{num_dice:d} die of {num_sides:d} sides")
@given("{num_dice:d} dice of {num_sides:d} sides")
def step_impl_given_dice(context, num_dice, num_sides):
    context.num_dice = num_dice
    context.num_sides = num_sides
    context.modifier = 0
    context.reroll_type = DiceRerollType.NONE


@given("a modifier of {modifier:d}")
def step_impl_given_modifier(context, modifier):
    context.modifier = modifier


@given("the roll has advantage")
def step_impl_given_advantage(context):
    context.reroll_type = DiceRerollType.ADVANTAGE


@given("the roll has disadvantage")
def step_impl_given_disadvantage(context):
    context.reroll_type = DiceRerollType.DISADVANTAGE


@when("I roll the dice")
def step_impl_when_roll(context):
    context.result = DiceRoller.roll(
        context.num_dice,
        context.num_sides,
        context.reroll_type,
        context.modifier,
    )


@then("the result should be between {min_val:d} and {max_val:d}")
def step_impl_then_range(context, min_val, max_val):
    assert min_val <= context.result.total <= max_val, (
        f"Result {context.result.total} not in range [{min_val}, {max_val}]"
    )


@then("{num_rolls:d} dice should be rolled")
def step_impl_then_num_rolls(context, num_rolls):
    assert len(context.result.results) == num_rolls, (
        f"Expected {num_rolls} rolls, got {len(context.result.results)}"
    )


@then("the total should be the highest die result")
def step_impl_then_highest(context):
    expected = max(context.result.results) + context.modifier
    assert context.result.total == expected, (
        f"Total {context.result.total} != expected highest {expected}"
    )


@then("the total should be the lowest die result")
def step_impl_then_lowest(context):
    expected = min(context.result.results) + context.modifier
    assert context.result.total == expected, (
        f"Total {context.result.total} != expected lowest {expected}"
    )


@then("the total should be the sum of the dice results")
def step_impl_then_sum(context):
    expected = sum(context.result.results) + context.modifier
    assert context.result.total == expected, (
        f"Total {context.result.total} != expected sum {expected}"
    )
