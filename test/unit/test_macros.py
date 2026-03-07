import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lib.macro.evaluator import MacroEvaluator, _safe_eval, evaluate_condition
from lib.macro.manager import MacroManager


class TestMacroManager(unittest.TestCase):
    """Test the macro manager parsing correctness."""

    def test_parse_simple_macro(self):
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "macros.txt"
            file_path.write_text(
                'defmacro test arg1:int arg2=default\n  echo("hello")\nendmacro\n'
            )
            manager = MacroManager(Path(tmpdir))
            manager.global_dir = Path(tmpdir)  # Prevent loading actual globals
            manager.load_macros()

            macro = manager.get_macro("test")
            self.assertIsNotNone(macro)
            if macro:
                self.assertEqual(len(macro.params), 2)
                self.assertEqual(macro.params[0].name, "arg1")
                self.assertEqual(macro.params[0].type_hint, "int")
                self.assertEqual(macro.params[1].name, "arg2")
                self.assertEqual(macro.params[1].default, "default")
                self.assertEqual(len(macro.body), 1)
                self.assertEqual(macro.body[0].func_name, "echo")
                self.assertEqual(macro.body[0].args[0].expr, "hello")


class TestMacroEvaluator(unittest.TestCase):
    """Test AST-based macro logic and expressions."""

    def test_safe_eval_math(self):
        context = {"a": 5, "b": 10}
        self.assertEqual(_safe_eval("a + b", context), 15)
        self.assertEqual(_safe_eval("a * b", context), 50)
        self.assertEqual(_safe_eval("b / 2", context), 5.0)

    def test_safe_eval_comparisons(self):
        context = {"a": 5, "b": 10}
        self.assertTrue(_safe_eval("a < b", context))
        self.assertFalse(_safe_eval("a > b", context))
        self.assertTrue(_safe_eval("a == 5 and b == 10", context))

    def test_safe_eval_undefined_variable(self):
        context = {"a": 5}
        with self.assertRaises(ValueError) as err:
            _safe_eval("a + missing_variable", context)
        self.assertIn("Undefined variable 'missing_variable'", str(err.exception))

    def test_macro_evaluation(self):
        from lib.macro.grammar import parse_macros

        text = (
            "defmacro test_macro val:int\n"
            "  my_var = val + 5\n"
            "  return my_var\n"
            "endmacro\n"
        )
        macros = parse_macros(text)
        macro = macros[0]
        evaluator = MacroEvaluator(macro, ["10"], lambda x: None, lambda x: None)
        self.assertEqual(evaluator.run(), 15)

    def test_evaluate_condition(self):
        context = {"val": 5}
        self.assertTrue(evaluate_condition("val == 5", context))
        self.assertFalse(evaluate_condition("val != 5", context))


if __name__ == "__main__":
    unittest.main()
