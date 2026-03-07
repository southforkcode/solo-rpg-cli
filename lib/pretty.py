import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any

from rich.console import Console


class PrettyPrinter:
    def __init__(self):
        self.console = Console()

    def can_print(self, obj: Any) -> bool:
        raise NotImplementedError

    def print(self, obj: Any) -> None:
        raise NotImplementedError


class PrettyPrinterRegistry:
    def __init__(self):
        self.printers = {}

    def register(self, obj: Any) -> None:
        self.printers[type(obj)] = obj

    def register_directory(self, directory: Path) -> None:
        for filename in directory.glob("*.py"):
            # load module and find all Command instances
            module_name = "lib.pretty_printers." + Path(filename).stem
            spec = importlib.util.spec_from_file_location(module_name, filename)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            classes = inspect.getmembers(module, inspect.isclass)
            for _, obj in classes:
                if issubclass(obj, PrettyPrinter) and obj != PrettyPrinter:
                    self.register(obj())

    def print(self, obj: Any) -> None:
        for printer in self.printers.values():
            if printer.can_print(obj):
                printer.print(obj)
                return
        console = Console()
        console.print(obj)
