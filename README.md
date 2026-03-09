# Solo RPG CLI

Solo RPG CLI is a command-line application designed to help you manage your solo tabletop role-playing game campaigns. It provides a suite of tools for tracking journeys, managing a campaign journal, rolling dice, and defining custom macros for complex game mechanics.

## Prerequisites

This project uses `uv` for dependency management and running the application. Make sure you have `uv` installed on your system.
See [astral-sh/uv](https://github.com/astral-sh/uv) for installation instructions.

## Building and Running

### Initialization

Before you can play, you need to initialize a game directory. This directory will store your campaign's data, including journals, journeys, and macros.

```bash
uv run python solo_rpg_cli.py <path/to/game/dir> --init
```

For example, to create a new game in a folder called `my_campaign`:
```bash
uv run python solo_rpg_cli.py my_campaign --init
```

### Running the CLI

To start the interactive REPL (Read-Eval-Print Loop) for your campaign, run:

```bash
uv run python solo_rpg_cli.py <path/to/game/dir>
```

This will drop you into the interactive prompt where you can execute commands like `journey`, `journal`, and `roll`. Type `help` within the CLI to see a list of available commands.

## Testing

The project includes both unit tests and feature (Behave) tests.

On **Linux/macOS**, use the Makefile:
```bash
make test
```

On **Windows**, run the provided batch script:
```console
test.bat
```

## Examples

Once in the REPL, you can run commands like:

```text
> journey start "Travel to Waterdeep"
> roll 1d20 + 4
> journal add "Met a mysterious stranger on the road."
> m play ambient
> summary
> macro list
```

For more detailed information on all commands and how to write macros, please see the [User Guide](doc/user_guide.md).

## Links

- [GitHub Repository](https://github.com/southforkcode/solo-rpg-cli)
- [Issue Tracker](https://github.com/southforkcode/solo-rpg-cli/issues)
