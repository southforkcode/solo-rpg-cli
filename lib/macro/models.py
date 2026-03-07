from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MacroParam:
    name: str
    type_hint: str
    default: Optional[str] = None


@dataclass
class Macro:
    name: str
    params: List[MacroParam]
    body: List[str]
    is_global: bool = False
