import sys
from pathlib import Path
from typing import Protocol

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console as RichConsole


class Console(Protocol):
    """Protocol defining the interface for I/O operations in the REPL."""

    def read(self) -> str:
        """Read a line of input from the user."""
        ...

    def print(self, text: str | object) -> None:
        """Print output to the user."""
        ...


class DefaultConsole:
    """Default implementation of Console using prompt_toolkit and rich."""

    def __init__(self, gamedir: Path):
        self.gamedir = gamedir
        self._session: PromptSession | None = None
        self._rich_console = RichConsole()

    @property
    def session(self) -> PromptSession:
        if self._session is None:
            self._session = PromptSession(
                history=FileHistory(str(self.gamedir / "history"))
            )
        return self._session

    def read(self) -> str:
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            print("> ", end="", flush=True)
            line = sys.stdin.readline()
            if not line:
                raise EOFError()
            return line.rstrip("\n")
        return self.session.prompt("> ")

    def print(self, text: str | object) -> None:
        # If it's a string, we print it directly. Otherwise let rich handle it or pass it on.
        self._rich_console.print(text)


class MockConsole:
    """Mock implementation of Console for testing purposes."""

    def __init__(self, inputs: list[str]):
        self.inputs = inputs
        self.outputs: list[str | object] = []

    def read(self) -> str:
        if not self.inputs:
            raise EOFError()
        return self.inputs.pop(0)

    def print(self, text: str | object) -> None:
        self.outputs.append(text)
