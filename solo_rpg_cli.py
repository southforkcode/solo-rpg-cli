from pathlib import Path

from lib.repl import REPLEnvironment

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
                f"Error: Directory '{args.gamedir}' already exists. "
                f"Cannot initialize."
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

    repl = REPLEnvironment(gamedir_path)
    repl.run()
    print("Bye!")
