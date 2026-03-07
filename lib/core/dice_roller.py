import random
from dataclasses import dataclass
from enum import Enum


class DiceRerollType(Enum):
    NONE = 0
    ADVANTAGE = 1
    DISADVANTAGE = 2


@dataclass
class DiceRoll:
    num_dice: int
    num_sides: int
    reroll_type: DiceRerollType = DiceRerollType.NONE
    modifier: int = 0

    def __str__(self):
        return (
            f"{self.num_dice}d{self.num_sides}/{self.reroll_type.name}/{self.modifier}"
        )


class DiceRollResult:
    def __init__(self, dice_roll: DiceRoll, results: list[int]):
        self.dice_roll = dice_roll
        self.results = results
        if dice_roll.reroll_type == DiceRerollType.ADVANTAGE:
            self.total = max(results) + dice_roll.modifier
        elif dice_roll.reroll_type == DiceRerollType.DISADVANTAGE:
            self.total = min(results) + dice_roll.modifier
        else:
            self.total = sum(results) + dice_roll.modifier

    def __str__(self):
        return f"{self.dice_roll} = {self.total} ({', '.join(map(str, self.results))})"


class DiceRoller:
    @classmethod
    def roll(
        cls,
        num_dice: int,
        num_sides: int,
        reroll_type: DiceRerollType = DiceRerollType.NONE,
        modifier: int = 0,
    ) -> DiceRollResult:
        assert num_dice > 0
        assert num_sides > 0
        assert reroll_type == DiceRerollType.NONE or num_dice == 1
        results = []
        for _ in range(num_dice):
            results.append(random.randint(1, num_sides))
        if reroll_type == DiceRerollType.ADVANTAGE:
            results.append(random.randint(1, num_sides))
        elif reroll_type == DiceRerollType.DISADVANTAGE:
            results.append(random.randint(1, num_sides))
        return DiceRollResult(
            DiceRoll(num_dice, num_sides, reroll_type, modifier),
            results,
        )
