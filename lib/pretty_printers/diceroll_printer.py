from rich.console import Console

from lib.dice_roller import DiceRollResult
from lib.pretty import PrettyPrinter


class DiceRollPrinter(PrettyPrinter):
    def can_print(self, obj: DiceRollResult) -> bool:
        return isinstance(obj, DiceRollResult)

    def print(self, obj: DiceRollResult) -> None:
        console = Console()
        console.print(f"{obj.total} ({', '.join(map(str, obj.results))})")
