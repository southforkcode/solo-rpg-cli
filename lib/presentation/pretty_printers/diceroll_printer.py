from rich.console import Console

from lib.core.dice_roller import DiceRollResult
from lib.presentation.pretty import PrettyPrinter


class DiceRollPrinter(PrettyPrinter):
    def can_print(self, obj: object) -> bool:
        return isinstance(obj, DiceRollResult)

    def print(self, obj: object) -> None:
        assert isinstance(obj, DiceRollResult)
        console = Console()
        console.print(
            f"[green]{obj.total} ({', '.join(map(str, obj.results))})[/green]"
        )
