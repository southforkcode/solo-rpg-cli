import ast
import operator
import re
from typing import Any, Callable, Dict, List, Tuple

from .models import Macro


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
        return self._execute_block(0, len(self.macro.body))

    def _execute_block(self, start: int, end: int) -> Any:
        """Execute a subset frame of the macro body lines."""
        i = start
        while i < end:
            line = self.macro.body[i].strip()
            if not line or line.startswith(";"):
                i += 1
                continue

            if line.startswith("if "):
                cond_str = line[3:]
                if cond_str.endswith("then"):
                    cond_str = cond_str[:-4].strip()
                condition_met = evaluate_condition(cond_str, self.context)

                # find block limits
                block_start = i + 1
                block_end, next_block_type, next_cond, end_if_idx = (
                    self._find_next_block(block_start, end)
                )

                if condition_met:
                    ret = self._execute_block(block_start, block_end)
                    if ret is not None:
                        return ret
                    i = end_if_idx + 1  # skip rest
                else:
                    # try else / elseif
                    handled = False
                    curr_type = next_block_type
                    curr_cond = next_cond
                    curr_start = block_end + 1

                    while curr_type in ("elseif", "else"):
                        next_end, next_type, n_cond, end_if_loc = self._find_next_block(
                            curr_start, end
                        )

                        if curr_type == "else" and not handled:
                            ret = self._execute_block(curr_start, next_end)
                            if ret is not None:
                                return ret
                            handled = True
                        elif curr_type == "elseif" and not handled:
                            if evaluate_condition(curr_cond, self.context):
                                ret = self._execute_block(curr_start, next_end)
                                if ret is not None:
                                    return ret
                                handled = True

                        curr_start = next_end + 1
                        curr_type = next_type
                        curr_cond = n_cond
                        if curr_type == "endif":
                            break

                    i = end_if_idx + 1
                continue

            ret = self._execute_line(line)
            if ret is not None:
                return ret
            i += 1
        return None

    def _find_next_block(self, start: int, end: int) -> Tuple[int, str, str, int]:
        """Skip through lines finding the extents and conditions for branches."""
        depth = 0
        block_end = end
        next_type = "endif"
        next_cond = ""
        end_if_idx = end

        for i in range(start, end):
            sub = self.macro.body[i].strip()
            if sub.startswith("if "):
                depth += 1
            elif sub == "endif":
                if depth == 0:
                    end_if_idx = i
                    if block_end == end:
                        block_end = i
                        next_type = "endif"
                    break
                else:
                    depth -= 1
            elif depth == 0:
                if sub.startswith("elseif "):
                    if block_end == end:
                        block_end = i
                        next_type = "elseif"
                        next_cond = sub[7:]
                        if next_cond.endswith("then"):
                            next_cond = next_cond[:-4].strip()
                elif sub == "else":
                    if block_end == end:
                        block_end = i
                        next_type = "else"

        # ensure end_if_idx is found
        if end_if_idx == end:
            for i in range(start, end):
                if self.macro.body[i].strip() == "endif" and depth == 0:
                    end_if_idx = i

        return block_end, next_type, next_cond, end_if_idx

    def _execute_line(self, line: str) -> Any:
        """Parse individual lines for evaluation against operations and bindings."""
        # assignments: var_name = func(...)
        # or just func(...)
        assign_match = re.match(r"^([a-zA-Z0-9_]+)\s*=\s*(.+)$", line)
        if assign_match:
            var_name = assign_match.group(1)
            expr = assign_match.group(2)
            val = self._eval_expr(expr)
            self.context[var_name] = val
        else:
            if line.startswith("return "):
                return self._eval_expr(line[7:].strip())
            else:
                self._eval_expr(line)
        return None

    def _eval_expr(self, expr: str) -> Any:
        """Parse interpolation variables and execute explicit builtin calls."""
        expr = interpolate(expr, self.context)

        # handle echo("...")
        echo_match = re.match(r"^echo\((.*)\)$", expr)
        if echo_match:
            content = echo_match.group(1)
            # strip quotes if present
            if (content.startswith('"') and content.endswith('"')) or (
                content.startswith("'") and content.endswith("'")
            ):
                content = content[1:-1]
            print(content)
            self.outputs.append(content)
            return None

        exec_match = re.match(r"^exec\((.*)\)$", expr)
        if exec_match:
            content = exec_match.group(1)
            if (content.startswith('"') and content.endswith('"')) or (
                content.startswith("'") and content.endswith("'")
            ):
                content = content[1:-1]
            return self.exec_cb(content)

        roll_match = re.match(r"^roll\((.*)\)$", expr)
        if roll_match:
            content = roll_match.group(1)
            if (content.startswith('"') and content.endswith('"')) or (
                content.startswith("'") and content.endswith("'")
            ):
                content = content[1:-1]
            return self.roll_cb(content)

        # fallback safe eval or just return the text
        try:
            return _safe_eval(expr, self.context)
        except ValueError as e:
            # Re-raise explicit ValueError from missing variables or unsupported ops
            if "Undefined variable" in str(e) or "Unsupported syntax" in str(e):
                raise
            return expr
        except Exception:
            return expr
