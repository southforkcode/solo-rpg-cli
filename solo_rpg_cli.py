from pathlib import Path

from lib.repl import REPLEnvironment

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Solo RPG CLI")
    parser.add_argument("gamedir", type=str, help="Path to the game directory")
    args = parser.parse_args()
    repl = REPLEnvironment(Path(args.gamedir))
    repl.run()
    print("Bye!")
