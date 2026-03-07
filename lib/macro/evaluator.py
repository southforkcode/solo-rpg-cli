import ast
import operator
import re
from typing import Any, Callable, Dict, List

from .models import (
    Assignment,
    EchoStatement,
    ExecStatement,
    Expression,
    IfStatement,
    Macro,
    ReturnStatement,
    RollStatement,
    Statement,
)


def interpolate(text: str, context: Dict[str, Any]) -> str:
    """Interpolate variables like ${var.prop} inside a string using the context."""

    def repl(match) -> str:
        var_path = match.group(1)
        parts = var_path.split(".")
        base = parts[0]
        if base in context:
            val = context[base]
            for p in parts[1:]:
                if hasattr(val, p):
                    val = getattr(val, p)
                elif isinstance(val, dict) and p in val:
                    val = val[p]
                else:
                    return str(match.group(0))
            return str(val)
        return str(match.group(0))

    return re.sub(r"\$\{([^}]+)\}", repl, text)


def _safe_eval(expr: str, context: Dict[str, Any]) -> Any:
    """Evaluate a python expression safely using AST parsing."""
    _mapping: Dict[Any, Any] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Not: operator.not_,
    }

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            raise ValueError(f"Undefined variable '{node.id}'")
        elif isinstance(node, ast.BinOp):
            return _mapping[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.Compare):
            left = _eval(node.left)
            for op, comp in zip(node.ops, node.comparators, strict=True):
                if not _mapping[type(op)](left, _eval(comp)):
                    return False
                left = _eval(comp)
            return True
        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(_eval(v) for v in node.values)
            else:
                return any(_eval(v) for v in node.values)
        elif isinstance(node, ast.UnaryOp):
            return _mapping[type(node.op)](_eval(node.operand))
        elif isinstance(node, ast.Attribute):
            val = _eval(node.value)
            if hasattr(val, node.attr):
                return getattr(val, node.attr)
            return None
        else:
            raise ValueError(f"Unsupported syntax in expression: {type(node).__name__}")

    try:
        expr = expr.strip()
        if not expr:
            return ""
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        # If AST parse fails (e.g. invalid syntax like '3d6'), return string
        return expr

    return _eval(tree)


def evaluate_condition(cond: str, context: Dict[str, Any]) -> bool:
    """Evaluate a conditional string and return its boolean value."""
    cond_eval = interpolate(cond, context).strip()
    try:
        return bool(_safe_eval(cond_eval, context))
    except Exception as e:
        raise ValueError(f"Error evaluating condition '{cond}': {e}") from e


class MacroEvaluator:
    """Evaluates the macro Abstract Syntax Tree contextually during runtime."""

    def __init__(
        self,
        macro: Macro,
        args: List[str],
        exec_cb: Callable[[str], Any],
        roll_cb: Callable[[str], Any],
    ) -> None:
        """Initialize parameters and evaluation callbacks."""
        self.macro = macro
        self.args = args
        self.exec_cb = exec_cb
        self.roll_cb = roll_cb
        self.context: Dict[str, Any] = {}
        self.outputs: List[str] = []
        self._bind_args()

    def _bind_args(self) -> None:
        """Parse arguments passed by the user against the macro's parameters."""
        for i, param in enumerate(self.macro.params):
            if i < len(self.args):
                val: Any = self.args[i]
            elif param.default is not None:
                val = param.default
            else:
                raise ValueError(f"Missing required argument: {param.name}")

            if param.type_hint == "int":
                try:
                    val = int(val)
                except ValueError:
                    raise ValueError(
                        f"Argument '{param.name}' must be an integer, got '{val}'"
                    ) from None
            elif param.type_hint == "float":
                try:
                    val = float(val)
                except ValueError:
                    raise ValueError(
                        f"Argument '{param.name}' must be a float, got '{val}'"
                    ) from None
            self.context[param.name] = val

    def run(self) -> Any:
        """Begin evaluating the core macro block."""
        return self._execute_block(self.macro.body)

    def _execute_block(self, block: List[Statement]) -> Any:
        """Execute a subset frame of the macro body lines."""
        for stmt in block:
            ret = self.visit(stmt)
            if ret is not None:
                # Assuming early return functionality
                return ret
        return None

    def visit(self, stmt: Statement) -> Any:
        if isinstance(stmt, IfStatement):
            return self.visit_IfStatement(stmt)
        elif isinstance(stmt, Assignment):
            return self.visit_Assignment(stmt)
        elif isinstance(stmt, EchoStatement):
            return self.visit_EchoStatement(stmt)
        elif isinstance(stmt, RollStatement):
            return self.visit_RollStatement(stmt)
        elif isinstance(stmt, ExecStatement):
            return self.visit_ExecStatement(stmt)
        elif isinstance(stmt, ReturnStatement):
            return self.visit_ReturnStatement(stmt)
        elif isinstance(stmt, Expression):
            return self.visit_Expression(stmt)
        else:
            raise ValueError(f"Unknown statement type: {type(stmt)}")

    def visit_IfStatement(self, stmt: IfStatement) -> Any:
        if evaluate_condition(stmt.condition.expr, self.context):
            return self._execute_block(stmt.if_body)

        for elif_block in stmt.elif_blocks:
            if evaluate_condition(elif_block.condition.expr, self.context):
                return self._execute_block(elif_block.body)

        if stmt.else_body is not None:
            return self._execute_block(stmt.else_body)

        return None

    def visit_Assignment(self, stmt: Assignment) -> Any:
        var_name = stmt.var_name
        val = self._eval_expr(stmt.expr.expr)
        self.context[var_name] = val
        return None

    def visit_EchoStatement(self, stmt: EchoStatement) -> Any:
        expr = interpolate(stmt.expr.expr, self.context)
        print(expr)
        self.outputs.append(expr)
        return None

    def visit_RollStatement(self, stmt: RollStatement) -> Any:
        expr = interpolate(stmt.expr.expr, self.context)
        return self.roll_cb(expr)

    def visit_ExecStatement(self, stmt: ExecStatement) -> Any:
        expr = interpolate(stmt.expr.expr, self.context)
        return self.exec_cb(expr)

    def visit_ReturnStatement(self, stmt: ReturnStatement) -> Any:
        return self._eval_expr(stmt.expr.expr)

    def visit_Expression(self, stmt: Expression) -> Any:
        # bare expression
        self._eval_expr(stmt.expr)
        return None

    def _eval_expr(self, expr_text: str) -> Any:
        """Parse interpolation variables and execute explicit builtin calls."""
        # For assignment and returns, if they embed roll, echo or exec we'll handle
        # them via regex fallback, but the grammar is now more strict, so this
        # acts to maintain backwards-compatibility with inline echo() etc inside
        # assignment if that was a thing, though the grammar primarily supports
        # them as Statements.

        expr_text = interpolate(expr_text, self.context)

        # handle inline echo(...)
        echo_match = re.match(r"^echo\((.*)\)$", expr_text)
        if echo_match:
            content = echo_match.group(1)
            if (content.startswith('"') and content.endswith('"')) or (
                content.startswith("'") and content.endswith("'")
            ):
                content = content[1:-1]
            print(content)
            self.outputs.append(content)
            return None

        exec_match = re.match(r"^exec\((.*)\)$", expr_text)
        if exec_match:
            content = exec_match.group(1)
            if (content.startswith('"') and content.endswith('"')) or (
                content.startswith("'") and content.endswith("'")
            ):
                content = content[1:-1]
            return self.exec_cb(content)

        roll_match = re.match(r"^roll\((.*)\)$", expr_text)
        if roll_match:
            content = roll_match.group(1)
            if (content.startswith('"') and content.endswith('"')) or (
                content.startswith("'") and content.endswith("'")
            ):
                content = content[1:-1]
            return self.roll_cb(content)

        # fallback safe eval or just return the text
        try:
            return _safe_eval(expr_text, self.context)
        except ValueError as e:
            # Re-raise explicit ValueError from missing variables or unsupported ops
            if "Undefined variable" in str(e) or "Unsupported syntax" in str(e):
                raise
            return expr_text
        except Exception:
            return expr_text
