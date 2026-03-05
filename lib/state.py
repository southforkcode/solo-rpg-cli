from typing import Any


class State:
    def __init__(self):
        self.state = {}
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
