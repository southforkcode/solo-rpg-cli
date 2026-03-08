from rich.console import Console

from lib.core.state import State
from lib.presentation.command import Command
from lib.presentation.lexer import Lexer


class VarCommand(Command):
    """Command to manage game variables (e.g., HP, Gold)."""

    def __init__(self):
        super().__init__()
        self.command = "var"
        self.aliases = ["variables", "v"]
        self.description = "Manage game variables"

    def get_completions(self, text_before_cursor: str, state: State) -> list[str]:
        """Return a list of autocomplete suggestions."""
        words = text_before_cursor.split()
        if not words:
            return []
            
        is_new_word = text_before_cursor.endswith(' ')
        verbs = ["set", "update", "get", "list", "delete"]
        
        if len(words) == 1 and not is_new_word:
            return []
            
        if len(words) == 1 and is_new_word:
            return verbs
            
        if len(words) == 2 and not is_new_word:
            prefix = words[1].lower()
            return [v for v in verbs if v.startswith(prefix)]
            
        verb = words[1].lower()
        if verb in ["set", "update", "get", "delete"]:
            vars_dict = state.variable_manager.get_all()
            var_names = list(vars_dict.keys())
            
            if len(words) == 2 and is_new_word:
                return var_names
                
            if len(words) == 3 and not is_new_word:
                prefix = words[2].lower()
                return [n for n in var_names if n.lower().startswith(prefix)]
                
        return []

    def execute(self, lexer: Lexer, state: State) -> object:
        subcmd = lexer.next()
        if not subcmd:
            self.help()
            return None

        if subcmd == "set":
            return self._execute_set(lexer, state)
        elif subcmd == "update":
            return self._execute_update(lexer, state)
        elif subcmd == "get":
            return self._execute_get(lexer, state)
        elif subcmd == "list":
            return self._execute_list(state)
        elif subcmd == "delete":
            return self._execute_delete(lexer, state)
        else:
            print(f"Unknown subcommand '{subcmd}' for var command.")
            self.help()
            return None

    def _execute_set(self, lexer: Lexer, state: State) -> object:
        """Create or update a variable with a parsed numeric or string value."""
        name = lexer.next()
        if not name:
            return "Usage: var set <name> <value>"

        # Gobble the remainder as the value
        value_str = ""
        while True:
            part = lexer.next()
            if not part:
                break
            value_str += (" " if value_str else "") + part

        if not value_str:
            return "Usage: var set <name> <value>"

        # Try to parse as int or float
        parsed_value: object = value_str
        try:
            parsed_value = int(value_str)
        except ValueError:
            try:
                parsed_value = float(value_str)
            except ValueError:
                pass

        state.variable_manager.set_var(name, parsed_value)
        return f"Variable '{name}' set to {parsed_value}."

    def _execute_update(self, lexer: Lexer, state: State) -> object:
        """Modify an existing numeric variable by a specified increment or decrement."""
        name = lexer.next()
        if not name:
            return "Usage: var update <name> <numeric_change>"

        change_str = lexer.next()
        if not change_str:
            return "Usage: var update <name> <numeric_change>"

        current_val = state.variable_manager.get_var(name)
        if current_val is None:
            return f"Variable '{name}' not found."

        try:
            change_val = int(change_str)
        except ValueError:
            try:
                change_val = float(change_str)  # type: ignore
            except ValueError:
                return f"Invalid numeric change: '{change_str}'"

        if not isinstance(current_val, (int, float)):
            return (
                f"Cannot update non-numeric variable '{name}' "
                f"(type: {type(current_val).__name__})"
            )

        new_val = current_val + change_val
        state.variable_manager.set_var(name, new_val)
        return f"Variable '{name}' updated to {new_val}."

    def _execute_get(self, lexer: Lexer, state: State) -> object:
        """Retrieve and format a specific variable's current value."""
        name = lexer.next()
        if not name:
            return "Usage: var get <name>"

        val = state.variable_manager.get_var(name)
        if val is None:
            return f"Variable '{name}' not found."

        # Don't return None because repl might not print it
        return f"{name}: {val}"

    def _execute_list(self, state: State) -> object:
        """List all currently tracked globally persisted game variables."""
        vars_dict = state.variable_manager.get_all()
        if not vars_dict:
            return "No variables defined."

        lines = ["Variables:"]
        for k, v in vars_dict.items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)

    def _execute_delete(self, lexer: Lexer, state: State) -> object:
        """Delete a given variable from the campaign state."""
        name = lexer.next()
        if not name:
            return "Usage: var delete <name>"

        console = state.get("console")
        if console and not console.confirm(f"Delete variable '{name}'?"):
            return "Cancelled."
            
        if state.variable_manager.delete_var(name):
            return f"Variable '{name}' deleted."
        else:
            return f"Variable '{name}' not found."

    def help(self):
        console = Console()
        console.print(
            "[bold cyan]var[/bold cyan] \\[[italic]subcommand[/italic]] "
            "\\[[italic]args...[/italic]]"
        )
        console.print("Manage game variables.")
        console.print("Subcommands:")
        console.print(
            "  [bold]set[/bold] [italic]<name>[/italic] [italic]<value>[/italic]"
            "       - Create or update a variable"
        )
        console.print(
            "  [bold]update[/bold] [italic]<name>[/italic] [italic]<change>[/italic]"
            "   - Add change to a numeric variable"
        )
        console.print(
            "  [bold]get[/bold] [italic]<name>[/italic]               "
            "- Print a specific variable"
        )
        console.print("  [bold]list[/bold]                     - List all variables")
        console.print(
            "  [bold]delete[/bold] [italic]<name>[/italic]            "
            "- Delete a variable"
        )
