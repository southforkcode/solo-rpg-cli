# Solo RPG CLI - Developer Guide

## Core Architecture

- **State Management (`lib/state.py`)**: `AppState` passes global state down via `Command.execute(lexer, state)`.
- **Journeys (`lib/journey.py`)**: The `JourneyManager` persists structured `Journey` instances (dataclasses) into `journeys.json`.
- **Journals (`lib/journal.py`)**: Flat-file `journal.txt` manager that adds timestamps and content headers.
- **Commands (`lib/commands/`):** Command classes (e.g., `JourneyCommand`, `JournalCommand`) inherit from `Command` and act as command-line routers relying on interactive prompts and a custom Lexer.
- **Printers (`lib/pretty_printers/`):** Dedicated classes handling the console output formatting (e.g., `JourneyPrinter`).

## Testing

Use `behave` tests via `make test` for end-to-end user-centric behavior verification.

## Extending

To add a new command:
1. Create a `NewCommand(Command)` class inside `lib/commands/`.
2. Provide `__init__(self)` mapping `self.command`, `self.aliases`, and `self.description`.
3. Implement `execute(self, lexer, state)` method.
4. Provide appropriate feature tests under `test/features/`.
