from pathlib import Path
from typing import Any

from lib.journal import JournalManager
from lib.journey import JourneyManager
from lib.macro import MacroManager
from lib.table import TableManager
from lib.variable import VariableManager


class State:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.journal_manager = JournalManager(base_dir)
        self.journey_manager = JourneyManager(base_dir)
        self.macro_manager = MacroManager(base_dir)
        self.table_manager = TableManager(base_dir)
        self.variable_manager = VariableManager(base_dir)
        self.state: dict[str, Any] = {}
        self.dirty = False

    def get(self, key: str) -> Any:
        return self.state.get(key)

    def set(self, key: str, value: Any) -> None:
        self.state[key] = value
        self.dirty = True

    def delete(self, key: str) -> None:
        del self.state[key]
        self.dirty = True

    def has(self, key: str) -> bool:
        return key in self.state

    def is_dirty(self) -> bool:
        return self.dirty

    def set_dirty(self, dirty: bool) -> None:
        self.dirty = dirty
