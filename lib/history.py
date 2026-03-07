from collections import deque
from datetime import datetime
from typing import Any


class HistoryItem:
    def __init__(self, command: str, result: Any, timestamp: float | None = None):
        self.command = command
        self.result = result
        self.timestamp = timestamp or datetime.now().timestamp()

    def __str__(self):
        return f"[{self.timestamp}] {self.command} = {self.result}"


class History:
    def __init__(self, maxlen: int = 10):
        self.history: deque[HistoryItem] = deque(maxlen=maxlen)

    def add(self, command: str, result: Any) -> None:
        self.history.append(HistoryItem(command, result))

    def get(self, offset: int) -> HistoryItem:
        if offset >= len(self.history):
            raise IndexError("Offset out of bounds")
        return self.history[-(offset + 1)]

    def get_all(self) -> list[HistoryItem]:
        return list(self.history)
