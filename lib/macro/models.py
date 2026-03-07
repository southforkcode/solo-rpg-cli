from dataclasses import dataclass
from typing import List, Optional


class Statement:
    """Base class for all macro statements."""

    pass


@dataclass
class Expression(Statement):
    expr: str


@dataclass
class Assignment(Statement):
    var_name: str
    expr: Expression


@dataclass
class ElifBlock:
    condition: Expression
    body: List[Statement]


@dataclass
class IfStatement(Statement):
    condition: Expression
    if_body: List[Statement]
    elif_blocks: List[ElifBlock]
    else_body: Optional[List[Statement]] = None


@dataclass
class ReturnStatement(Statement):
    expr: Expression


@dataclass
class EchoStatement(Statement):
    expr: Expression


@dataclass
class RollStatement(Statement):
    expr: Expression


@dataclass
class ExecStatement(Statement):
    expr: Expression


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
    body: List[Statement]
    is_global: bool = False
