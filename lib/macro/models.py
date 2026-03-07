from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MacroParam:
    """Represents a single parameter defined in a macro."""

    name: str
    type_hint: str
    default: Optional[str] = None


@dataclass
class Macro:
    """Represents a parsed macro definition including its arguments and body."""

    name: str
    params: List[MacroParam]
    body: List[str]
    is_global: bool = False
