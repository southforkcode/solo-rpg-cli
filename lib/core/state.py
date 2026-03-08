from pathlib import Path
from typing import Any

from lib.core.journal import JournalManager
from lib.core.journey import JourneyManager
from lib.core.macro import MacroManager
from lib.core.settings import SettingsManager
from lib.core.table import TableManager
from lib.core.variable import VariableManager


class State:
    def __init__(
        self,
        base_dir: Path,
        journal_manager: JournalManager,
        journey_manager: JourneyManager,
        macro_manager: MacroManager,
        settings_manager: SettingsManager,
        table_manager: TableManager,
        variable_manager: VariableManager,
    ):
        self.base_dir = base_dir
        self.journal_manager = journal_manager
        self.journey_manager = journey_manager
        self.macro_manager = macro_manager
        self.settings_manager = settings_manager
        self.table_manager = table_manager
        self.variable_manager = variable_manager
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


class StateFactory:
    @staticmethod
    def create(base_dir: Path) -> "State":
        settings_manager = SettingsManager(base_dir)
        return State(
            base_dir=base_dir,
            journal_manager=JournalManager(base_dir),
            journey_manager=JourneyManager(base_dir),
            macro_manager=MacroManager(base_dir),
            settings_manager=settings_manager,
            table_manager=TableManager(base_dir, settings_manager),
            variable_manager=VariableManager(base_dir),
        )
