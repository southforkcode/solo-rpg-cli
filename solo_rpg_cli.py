from pathlib import Path

from lib.presentation.repl import REPLEnvironment

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Solo RPG CLI")
    parser.add_argument("gamedir", type=str, help="Path to the game directory")
    parser.add_argument(
        "--init", action="store_true", help="Initialize a new game directory"
    )
    args = parser.parse_args()

    gamedir_path = Path(args.gamedir)

    if args.init:
        if gamedir_path.exists():
            print(
                f"Error: Directory '{args.gamedir}' already exists. Cannot initialize."
            )
            sys.exit(1)
        else:
            gamedir_path.mkdir(parents=True)
            print(f"Initialized new game directory at '{args.gamedir}'.")
    else:
        if not gamedir_path.exists():
            print(
                f"Error: Game directory '{args.gamedir}' not found. "
                f"Use --init to create and initialize it."
            )
            sys.exit(1)

    from lib.core.journal import JournalManager
    from lib.core.journey import JourneyManager
    from lib.core.macro import MacroManager
    from lib.core.settings import SettingsManager
    from lib.core.state import State
    from lib.core.table import TableManager
    from lib.core.variable import VariableManager
    from lib.presentation.commands.journal_command import JournalCommand
    from lib.presentation.commands.journey_command import JourneyCommand
    from lib.presentation.commands.macro_command import MacroCommand
    from lib.presentation.commands.oracle_command import OracleCommand
    from lib.presentation.commands.roll_command import RollCommand
    from lib.presentation.commands.summary_command import SummaryCommand
    from lib.presentation.commands.table_command import TableCommand
    from lib.presentation.commands.var_command import VarCommand

    journal_mgr = JournalManager(gamedir_path)
    journey_mgr = JourneyManager(gamedir_path)
    macro_mgr = MacroManager(gamedir_path)
    settings_mgr = SettingsManager(gamedir_path)
    table_mgr = TableManager(gamedir_path, settings_mgr)
    var_mgr = VariableManager(gamedir_path)

    state = State(
        base_dir=gamedir_path,
        journal_manager=journal_mgr,
        journey_manager=journey_mgr,
        macro_manager=macro_mgr,
        settings_manager=settings_mgr,
        table_manager=table_mgr,
        variable_manager=var_mgr,
    )

    repl = REPLEnvironment(gamedir_path, state)

    repl.command_registry.register(JournalCommand())
    repl.command_registry.register(JourneyCommand())
    repl.command_registry.register(MacroCommand())
    repl.command_registry.register(OracleCommand())
    repl.command_registry.register(RollCommand())
    repl.command_registry.register(SummaryCommand())
    repl.command_registry.register(TableCommand())
    repl.command_registry.register(VarCommand())

    repl.pretty_printer_registry.register_directory(
        Path("lib/presentation/pretty_printers")
    )
    repl.run()
    print("Bye!")
