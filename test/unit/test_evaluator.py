import unittest

from lib.core.macro.evaluator import _safe_eval, interpolate, evaluate_condition, MacroEvaluator
from lib.core.macro.models import Macro, Statement, Assignment, Expression, ReturnStatement, CallStatement
from lib.core.macro.models import MacroParam

class TestEvaluator(unittest.TestCase):
    def test_interpolate(self):
        context = {"hero": {"name": "Bob", "stats": {"hp": 10}}, "dmg": 5}
        res = interpolate("Hero ${hero.name} takes ${dmg} damage, hp is ${hero.stats.hp}!", context)
        self.assertEqual(res, "Hero Bob takes 5 damage, hp is 10!")
        
    def test_safe_eval(self):
        import types
        obj = types.SimpleNamespace(x=5)
        ctx = {"a": 10, "b": 20, "c": True, "d": obj}
        self.assertEqual(_safe_eval("a + b", ctx), 30)
        self.assertEqual(_safe_eval("a * 2 - 5", ctx), 15)
        self.assertEqual(_safe_eval("a > 5 and b < 30", ctx), True)
        self.assertEqual(_safe_eval("not c", ctx), False)
        self.assertEqual(_safe_eval("d.x", ctx), 5)
        self.assertIsNone(_safe_eval("d.y", ctx))
        
    def test_evaluate_condition(self):
        ctx = {"hp": 0}
        self.assertTrue(evaluate_condition("hp <= 0", ctx))
        self.assertFalse(evaluate_condition("hp > 0", ctx))
        with self.assertRaises(ValueError):
            evaluate_condition("missing_var > 0", ctx)

    def test_macro_evaluator_basic(self):
        m = Macro(
            name="test",
            params=[MacroParam("x", "int", None), MacroParam("y", "int", "5")],
            body=[]
        )
        
        # Test bind args
        evaluator = MacroEvaluator(m, ["10"], lambda x: x, lambda x: x)
        self.assertEqual(evaluator.context["x"], 10)
        self.assertEqual(evaluator.context["y"], 5)
        
        # Test Assignment and Return
        from lib.core.macro.models import Assignment, ReturnStatement, Expression
        assign = Assignment("z", Expression("x + y"))
        ret = ReturnStatement(Expression("z * 2"))
        m.body = [assign, ret]
        
        evaluator = MacroEvaluator(m, ["10"], lambda x: x, lambda x: x)
        res = evaluator.run()
        self.assertEqual(res, 30)

    def test_inline_functions(self):
        m = Macro(name="test", params=[], body=[])
        evaluator = MacroEvaluator(m, [], lambda x: f"exec_{x}", lambda x: f"roll_{x}")
        
        evaluator._eval_expr('echo("Hello")')
        self.assertIn("Hello", evaluator.outputs)
        
        self.assertEqual(evaluator._eval_expr('roll("1d20")'), "roll_1d20")
        self.assertEqual(evaluator._eval_expr('exec("cmd")'), "exec_cmd")
        
        # Valid Python fallback
        self.assertEqual(evaluator._eval_expr('10 + 20'), 30)

    def test_if_statement(self):
        from lib.core.macro.models import IfStatement, ElifBlock, Assignment, Expression
        m = Macro(name="test", params=[MacroParam("x", "int", None)], body=[])
        
        # Test if x > 5: z = 10, else: z = 20
        assign_if = Assignment("z", Expression("10"))
        assign_else = Assignment("z", Expression("20"))
        if_stmt = IfStatement(
            condition=Expression("x > 5"),
            if_body=[assign_if],
            elif_blocks=[],
            else_body=[assign_else]
        )
        m.body = [if_stmt]
        
        # x = 10 -> z should be 10
        eval1 = MacroEvaluator(m, ["10"], lambda x: x, lambda x: x)
        eval1.run()
        self.assertEqual(eval1.context.get("z"), 10)
        
        # x = 3 -> z should be 20
        eval2 = MacroEvaluator(m, ["3"], lambda x: x, lambda x: x)
        eval2.run()
        self.assertEqual(eval2.context.get("z"), 20)

    def test_evaluator_errors(self):
        m = Macro(name="test", params=[MacroParam("x", "int", None)], body=[])
        # Missing required argument
        with self.assertRaises(ValueError):
            MacroEvaluator(m, [], lambda x: x, lambda x: x)
            
        m2 = Macro(name="test", params=[], body=[])
        eval_err = MacroEvaluator(m2, [], lambda x: x, lambda x: x)
        from lib.core.macro.models import CallStatement, Expression
        call_unknown = CallStatement(func_name="unknown_func", args=[Expression("1")])
        with self.assertRaises(ValueError):
            eval_err.visit_CallStatement(call_unknown)

