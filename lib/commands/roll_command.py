from typing import Any

from lib.command import Command
from lib.dice_roller import DiceRerollType, DiceRoller
from lib.lexer import Lexer
from lib.state import State


class RollCommand(Command):
    def __init__(self):
        super().__init__()
        self.command = "roll"
        self.aliases = ["r"]
        self.description = "Roll dice"

    def execute(self, lexer: Lexer, state: State) -> Any:
        dice = lexer.next()
        if dice is None:
            raise SyntaxError("roll <dice> [adv|dis] [modifier] - Roll dice")
        # parse dice string - [<num_dice>]d<num_sides>
        if "d" not in dice:
            raise SyntaxError("roll <dice> [adv|dis] [modifier] - Roll dice")
        parts = dice.split("d")
        if len(parts) != 2:
            raise SyntaxError("roll <dice> [adv|dis] [modifier] - Roll dice")
        num_dice = int(parts[0] or "1")
        num_sides = int(parts[1])
        reroll_type = DiceRerollType.NONE
        modifier = 0
        modifier_str = None
        adv_dis = lexer.next()
        if adv_dis is not None:
            if adv_dis == "adv":
                reroll_type = DiceRerollType.ADVANTAGE
                modifier_str = lexer.next()
            elif adv_dis == "dis":
                reroll_type = DiceRerollType.DISADVANTAGE
                modifier_str = lexer.next()
            else:
                modifier_str = adv_dis
        if modifier_str is not None:
            if modifier_str in ("+", "-"):
                val_str = lexer.next()
                if val_str is None:
                    raise SyntaxError("roll <dice> [adv|dis] [modifier] - Roll dice")
                val = int(val_str)
                modifier = val if modifier_str == "+" else -val
            else:
                raise SyntaxError("roll <dice> [adv|dis] [modifier] - Roll dice")
        result = DiceRoller.roll(num_dice, num_sides, reroll_type, modifier)
        return result

    def help(self) -> None:
        print("roll <dice> [adv|dis] [modifier] - Roll dice")
        print("  <dice> - Number of dice to roll (e.g. 3d6, d20)")
        print("  [adv|dis] - Advantage or disadvantage")
        print("  [modifier] - Modifier to add to the roll (e.g. +4, -2)")
        print("Examples:")
        print("    roll 3d6")
        print("    roll d20 adv")
        print("    roll 2d6 + 4")
