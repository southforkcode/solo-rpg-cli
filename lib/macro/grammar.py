from typing import List

from parsimonious.grammar import Grammar
from parsimonious.nodes import Node, NodeVisitor

from .models import (
    Assignment,
    EchoStatement,
    ElifBlock,
    ExecStatement,
    Expression,
    IfStatement,
    Macro,
    MacroParam,
    ReturnStatement,
    RollStatement,
    Statement,
)

MACRO_GRAMMAR = Grammar(
    r"""
    program = (macro_def / empty_line / comment)*

    macro_def = _ "defmacro" _ ident _ params? _nl statements _ "endmacro" _nl?

    params = param+
    param = _ ident (":" type_hint)? ("=" default_val)?
    type_hint = ~r"[a-zA-Z_]\w*"
    default_val = ~r"[^\s]+"

    statements = (statement / empty_line / comment)*

    statement = _ (
        if_block
        / return_stmt
        / assignment
        / echo_stmt
        / roll_stmt
        / exec_stmt
        / bare_expr
    ) _nl?

    if_block = if_stmt elif_stmts* else_stmt? _ "endif"
    if_stmt = "if" _ expr_cond _ ("then" _)? _nl statements
    elif_stmts = _ "elseif" _ expr_cond _ ("then" _)? _nl statements
    else_stmt = _ "else" _nl statements

    return_stmt = "return" _ expr_rest
    assignment = ident _ "=" _ expr_rest

    echo_stmt = "echo(" string_arg ")"
    roll_stmt = "roll(" string_arg ")"
    exec_stmt = "exec(" string_arg ")"

    string_arg = ("\"" ~r"[^\"]*" "\"") / ("'" ~r"[^']*" "'")

    bare_expr = !keywords expr_rest

    keywords = "endmacro" / "endif" / "else" / "elseif" / "if"

    expr_cond = expr_cond_part+
    expr_cond_part = ~r"[^\r\n]+"

    expr_rest = ~r"[^\r\n]+"

    ident = ~r"[a-zA-Z_]\w*"

    comment = _ ~r";.*" _nl?
    empty_line = _ _nl

    _ = ~r"[ \t]*"
    _nl = ~r"[\r\n]+"
    """
)


class MacroVisitor(NodeVisitor):
    def visit_program(self, node: Node, visited_children: list) -> List[Macro]:
        return [c[0] for c in visited_children if isinstance(c[0], Macro)]

    def visit_macro_def(self, node: Node, visited_children: list) -> Macro:
        _, _, _, name_node, _, params_node, _, stmts, _, _, _ = visited_children
        name = name_node

        params = []
        if isinstance(params_node, list) and len(params_node) > 0:
            params = params_node[0]

        filtered_stmts = [s for s in stmts if isinstance(s, Statement)]

        return Macro(name=name, params=params, body=filtered_stmts)

    def visit_params(self, node: Node, visited_children: list) -> List[MacroParam]:
        return visited_children

    def visit_param(self, node: Node, visited_children: list) -> MacroParam:
        _, name, type_hint_node, default_val_node = visited_children

        type_hint = "str"
        if isinstance(type_hint_node, list) and len(type_hint_node) > 0:
            type_hint = type_hint_node[0][1]

        default = None
        if isinstance(default_val_node, list) and len(default_val_node) > 0:
            default = default_val_node[0][1]

        return MacroParam(name=name, type_hint=type_hint, default=default)

    def visit_type_hint(self, node: Node, visited_children: list) -> str:
        return node.text

    def visit_default_val(self, node: Node, visited_children: list) -> str:
        return node.text

    def visit_statements(self, node: Node, visited_children: list) -> List[Statement]:
        return [c[0] for c in visited_children if isinstance(c[0], Statement)]

    def visit_statement(self, node: Node, visited_children: list) -> Statement:
        _, stmt, _ = visited_children
        return stmt[0]

    def visit_if_block(self, node: Node, visited_children: list) -> IfStatement:
        if_stmt, elifs, else_stmt, _, _ = visited_children

        condition = if_stmt["condition"]
        if_body = if_stmt["body"]

        else_body = None
        if isinstance(else_stmt, list) and len(else_stmt) > 0:
            else_body = else_stmt[0]

        return IfStatement(
            condition=condition, if_body=if_body, elif_blocks=elifs, else_body=else_body
        )

    def visit_if_stmt(self, node: Node, visited_children: list) -> dict:
        _, _, expr, _, _, _, stmts = visited_children
        return {"condition": expr, "body": stmts}

    def visit_elif_stmts(self, node: Node, visited_children: list) -> ElifBlock:
        _, _, _, expr, _, _, _, stmts = visited_children
        return ElifBlock(condition=expr, body=stmts)

    def visit_else_stmt(self, node: Node, visited_children: list) -> List[Statement]:
        _, _, _, stmts = visited_children
        return stmts

    def visit_return_stmt(self, node: Node, visited_children: list) -> ReturnStatement:
        _, _, expr = visited_children
        return ReturnStatement(expr=expr)

    def visit_assignment(self, node: Node, visited_children: list) -> Assignment:
        ident, _, _, _, expr = visited_children
        return Assignment(var_name=ident, expr=expr)

    def visit_echo_stmt(self, node: Node, visited_children: list) -> EchoStatement:
        _, arg, _ = visited_children
        return EchoStatement(expr=Expression(expr=arg))

    def visit_roll_stmt(self, node: Node, visited_children: list) -> RollStatement:
        _, arg, _ = visited_children
        return RollStatement(expr=Expression(expr=arg))

    def visit_exec_stmt(self, node: Node, visited_children: list) -> ExecStatement:
        _, arg, _ = visited_children
        return ExecStatement(expr=Expression(expr=arg))

    def visit_string_arg(self, node: Node, visited_children: list) -> str:
        # Strip quotes
        text = node.text
        if (text.startswith('"') and text.endswith('"')) or (
            text.startswith("'") and text.endswith("'")
        ):
            return text[1:-1]
        return text

    def visit_bare_expr(self, node: Node, visited_children: list) -> Expression:
        _, expr = visited_children
        return expr

    def visit_expr_cond(self, node: Node, visited_children: list) -> Expression:
        # Stop at " then" or basically we need to make sure expr strips correctly
        t = node.text.strip()
        if t.endswith(" then"):
            t = t[:-5].strip()
        return Expression(expr=t)

    def visit_expr_rest(self, node: Node, visited_children: list) -> Expression:
        return Expression(expr=node.text.strip())

    def visit_ident(self, node: Node, visited_children: list) -> str:
        return node.text

    def visit_keywords(self, node: Node, visited_children: list) -> str:
        return node.text

    def visit_expr_cond_part(self, node: Node, visited_children: list) -> str:
        return node.text

    def visit_comment(self, node: Node, visited_children: list) -> None:
        return None

    def visit_empty_line(self, node: Node, visited_children: list) -> None:
        return None

    def generic_visit(self, node: Node, visited_children: list) -> list:
        return visited_children or node


def parse_macros(text: str) -> List[Macro]:
    if not text.strip():
        return []
    # Ensure text ends with a newline to satisfy the grammar empty lines
    if not text.endswith("\n"):
        text += "\n"
    tree = MACRO_GRAMMAR.parse(text)
    visitor = MacroVisitor()
    macros = visitor.visit(tree)
    if isinstance(macros, Macro):
        return [macros]
    return macros
