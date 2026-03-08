from typing import Iterable

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

from lib.core.state import State
from lib.presentation.command import CommandRegistry


class REPLCompleter(Completer):
    """Custom completer for the REPL prompt giving context-aware completions."""

    def __init__(self, registry: CommandRegistry, state: State):
        self.registry = registry
        self.state = state

    def get_completions(
        self, document: Document, complete_event
    ) -> Iterable[Completion]:
        text_before_cursor = document.text_before_cursor

        words = text_before_cursor.split()
        if not text_before_cursor:
            # offer base commands
            for cmd in self.registry.commands:
                yield Completion(cmd.command, start_position=0)

            # also offer macros
            manager = getattr(self.state, "macro_manager", None)
            if manager:
                for m in manager.list_macros():
                    yield Completion(f"/{m.name}", start_position=0)
            return

        is_new_word = text_before_cursor.endswith(" ")

        if len(words) == 1 and not is_new_word:
            # Complete the root command
            prefix = words[0].lower()
            for cmd in self.registry.commands:
                if cmd.command.startswith(prefix):
                    yield Completion(cmd.command, start_position=-len(prefix))
                for alias in cmd.aliases:
                    if alias.startswith(prefix):
                        yield Completion(alias, start_position=-len(prefix))

            # Offer macros
            if prefix.startswith("/") or prefix.startswith("//"):
                is_journal = prefix.startswith("//")
                macro_prefix = prefix[2:] if is_journal else prefix[1:]
                manager = getattr(self.state, "macro_manager", None)
                if manager:
                    for m in manager.list_macros():
                        if m.name.startswith(macro_prefix):
                            full_macro = f"//{m.name}" if is_journal else f"/{m.name}"
                            yield Completion(full_macro, start_position=-len(prefix))
            return

        # We are typing arguments for a command
        root_command_str = words[0]
        # check if it's a macro
        if root_command_str.startswith("/"):
            return

        found_cmd = self.registry.lookup_command(root_command_str)
        if found_cmd:
            completions = found_cmd.get_completions(text_before_cursor, self.state)

            current_word = "" if is_new_word else words[-1]
            for comp in completions:
                # Provide only case-insensitive prefix matches for the current word
                if comp.lower().startswith(current_word.lower()):
                    yield Completion(comp, start_position=-len(current_word))
