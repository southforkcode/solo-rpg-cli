import json
import random

from rich.console import Console

from lib.core.state import State
from lib.presentation.command import Command
from lib.presentation.lexer import Lexer


class OracleCommand(Command):
    """
    A command to simulate a virtual GM answering yes/no questions.

    This command allows users to ask a question and specify the odds of a 'Yes'
    answer using predefined labels (e.g., likely, unlikely, certain). It can
    also read custom probabilities from an 'oracle.json' file.
    """

    DEFAULT_ODDS = {
        "certain": 90,
        "likely": 75,
        "50/50": 50,
        "unlikely": 25,
        "impossible": 10,
    }

    def __init__(self):
        super().__init__()
        self.command = "oracle"
        self.aliases = ["o"]
        self.description = (
            "Ask the oracle a question. "
            'Syntax: oracle ["Question"] [--odds <likelihood>]'
        )

    def execute(self, lexer: Lexer, state: State) -> object:
        """
        Executes the oracle command.

        Args:
            lexer (Lexer): The lexer containing the command arguments.
            state (State): The current game state, used to resolve base paths.

        Returns:
            str: The formatted oracle answer ("Oracle: Yes" or "Oracle: No"),
                 optionally including the asked question.

        Raises:
            SyntaxError: If the --odds flag is provided without a value.
        """
        question = ""
        odds_key = "50/50"
        args_provided = False

        # Parse arguments
        while True:
            token = lexer.next()
            if token is None:
                break

            args_provided = True

            if token == "--odds":
                next_token = lexer.next()
                if next_token is None:
                    raise SyntaxError(
                        'oracle ["Question"] [--odds <likelihood>] - '
                        "expected likelihood after --odds"
                    )
                odds_key = next_token
            else:
                # If it's not a flag, treat it as part of the question.
                # If there are multiple tokens not tied to flags,
                # join them intelligently.
                if question:
                    if len(token) == 1 and token in "?!.":
                        question += token
                    else:
                        question += " " + token
                else:
                    question = token

        # Load probability table
        odds_table = self.DEFAULT_ODDS.copy()
        config_path = state.base_dir / "oracle.json"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    custom_odds = json.load(f)
                    if isinstance(custom_odds, dict):
                        odds_table.update(custom_odds)
            except Exception as e:
                print(f"Warning: Failed to load oracle.json: {e}")

        # If no arguments were provided at all, dump the table and return
        if not question and odds_key == "50/50" and not args_provided:
            lines = ["Oracle Probability Table:"]
            for k, v in odds_table.items():
                lines.append(f"  {k}: {v}%")
            return "\n".join(lines)

        # Ensure chosen odds_key exists
        if odds_key not in odds_table:
            print(f"Warning: Unknown odds '{odds_key}'. Falling back to '50/50'.")
            print(f"Available odds: {', '.join(odds_table.keys())}")
            odds_key = "50/50"

        target_number = odds_table[odds_key]

        # Roll 1d100
        roll = random.randint(1, 100)
        answer = "Yes" if roll <= target_number else "No"

        # Format output
        output = f"Oracle: {answer}"
        if question:
            output = f"Oracle: {answer} (Question: {question})"

        return output

    def help(self) -> None:
        console = Console()
        console.print(
            '[bold cyan]oracle[/bold cyan] \\[[italic]"Question"[/italic]] '
            "\\[[bold]--odds[/bold] [italic]<likelihood>[/italic]] - Ask the "
            "oracle a yes/no question"
        )
        console.print('  [italic]"Question"[/italic] - Optional question to ask')
        console.print(
            "  [bold]--odds[/bold] [italic]<likelihood>[/italic] - Optional "
            "probability of a Yes answer."
        )
        console.print(
            "                          Defaults to 50/50. Common options: "
            "certain, likely, 50/50, unlikely, impossible."
        )
        console.print("Examples:")
        console.print('    oracle "Are there guards?" --odds likely')
        console.print('    oracle "Is the chest locked?"')
        console.print("    o --odds certain")
