"""Unit tests for the safe_eval module."""

import ast
import unittest
from types import SimpleNamespace

from src.payroll_tax_calculator.safe_eval import (
    SafeEvalError,
    _to_namespace,
    _Validator,
    compile_safe_expr,
    safe_eval,
)


class TestSafeEval(unittest.TestCase):
    """Test cases for the safe_eval module."""

    def test_to_namespace(self):
        """Test _to_namespace function."""
        # Test with a simple dict
        data = {"a": 1, "b": 2}
        ns = _to_namespace(data)
        self.assertIsInstance(ns, SimpleNamespace)
        self.assertEqual(ns.a, 1)
        self.assertEqual(ns.b, 2)

        # Test with nested dict
        data = {"a": {"b": {"c": 3}}}
        ns = _to_namespace(data)
        self.assertIsInstance(ns, SimpleNamespace)
        self.assertIsInstance(ns.a, SimpleNamespace)
        self.assertIsInstance(ns.a.b, SimpleNamespace)
        self.assertEqual(ns.a.b.c, 3)

        # Test with non-dict
        data = 42
        result = _to_namespace(data)
        self.assertEqual(result, 42)

        # Test with mixed types
        data = {"a": 1, "b": {"c": 3}, "d": [1, 2, 3]}
        ns = _to_namespace(data)
        self.assertIsInstance(ns, SimpleNamespace)
        self.assertEqual(ns.a, 1)
        self.assertIsInstance(ns.b, SimpleNamespace)
        self.assertEqual(ns.b.c, 3)
        self.assertEqual(ns.d, [1, 2, 3])  # Lists should remain lists

    def test_validator(self):
        """Test _Validator class."""
        validator = _Validator()

        # Test allowed node
        node = ast.Constant(value=42)
        validator.visit(node)  # Should not raise

        # Test disallowed node
        node = ast.AsyncFunctionDef(name="test", args=None, body=[], decorator_list=[])
        with self.assertRaises(SafeEvalError) as context:
            validator.visit(node)
        self.assertIn("Disallowed expression node", str(context.exception))

        # Test allowed unary operator
        node = ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=42))
        validator.visit(node)  # Should not raise

        # Test disallowed unary operator (create a fake one for testing)
        class FakeUnaryOp(ast.unaryop):
            pass

        node = ast.UnaryOp(op=FakeUnaryOp(), operand=ast.Constant(value=42))
        with self.assertRaises(SafeEvalError) as context:
            validator.visit(node)
        self.assertIn("Disallowed unary operator", str(context.exception))

        # Test attribute access
        node = ast.Attribute(
            value=ast.Name(id="obj", ctx=ast.Load()), attr="normal", ctx=ast.Load()
        )
        validator.visit(node)  # Should not raise

        # Test private attribute access
        node = ast.Attribute(
            value=ast.Name(id="obj", ctx=ast.Load()), attr="_private", ctx=ast.Load()
        )
        with self.assertRaises(SafeEvalError) as context:
            validator.visit(node)
        self.assertIn(
            "Access to private attributes is forbidden", str(context.exception)
        )

        # Test dunder attribute access
        node = ast.Attribute(
            value=ast.Name(id="obj", ctx=ast.Load()), attr="__class__", ctx=ast.Load()
        )
        with self.assertRaises(SafeEvalError) as context:
            validator.visit(node)
        self.assertIn(
            "Access to private attributes is forbidden", str(context.exception)
        )

    def test_safe_eval_literals(self):
        """Test safe_eval with literal values."""
        # Test with integer
        self.assertEqual(safe_eval(42), 42)

        # Test with float
        self.assertEqual(safe_eval(3.14), 3.14)

        # Test with boolean
        self.assertEqual(safe_eval(True), True)
        self.assertEqual(safe_eval(False), False)

        # Test with None
        self.assertEqual(safe_eval(None), None)

    def test_safe_eval_simple_expressions(self):
        """Test safe_eval with simple expressions."""
        # Test basic arithmetic
        self.assertEqual(safe_eval("2 + 3"), 5)
        self.assertEqual(safe_eval("5 - 2"), 3)
        self.assertEqual(safe_eval("3 * 4"), 12)
        self.assertEqual(safe_eval("10 / 2"), 5.0)
        self.assertEqual(safe_eval("10 // 3"), 3)
        self.assertEqual(safe_eval("10 % 3"), 1)
        self.assertEqual(safe_eval("2 ** 3"), 8)

        # Test unary operators
        self.assertEqual(safe_eval("+5"), 5)
        self.assertEqual(safe_eval("-5"), -5)
        self.assertEqual(safe_eval("not True"), False)
        self.assertEqual(safe_eval("not False"), True)

        # Test boolean operators
        self.assertEqual(safe_eval("True and True"), True)
        self.assertEqual(safe_eval("True and False"), False)
        self.assertEqual(safe_eval("True or False"), True)
        self.assertEqual(safe_eval("False or False"), False)

        # Test comparison operators
        self.assertEqual(safe_eval("2 == 2"), True)
        self.assertEqual(safe_eval("2 != 3"), True)
        self.assertEqual(safe_eval("2 < 3"), True)
        self.assertEqual(safe_eval("3 > 2"), True)
        self.assertEqual(safe_eval("2 <= 2"), True)
        self.assertEqual(safe_eval("2 >= 2"), True)

    def test_safe_eval_with_allowed_functions(self):
        """Test safe_eval with allowed functions."""
        # Test abs
        self.assertEqual(safe_eval("abs(-5)"), 5)

        # Test math functions
        self.assertEqual(safe_eval("ceil(3.1)"), 4)
        self.assertEqual(safe_eval("floor(3.9)"), 3)
        self.assertEqual(safe_eval("round(3.5)"), 4)
        self.assertEqual(safe_eval("sqrt(9)"), 3.0)

        # Test min/max
        self.assertEqual(safe_eval("min(1, 2, 3)"), 1)
        self.assertEqual(safe_eval("max(1, 2, 3)"), 3)

    def test_safe_eval_with_allowed_constants(self):
        """Test safe_eval with allowed constants."""
        # Test true/false/null
        self.assertEqual(safe_eval("true"), True)
        self.assertEqual(safe_eval("false"), False)
        self.assertEqual(safe_eval("null"), None)

    def test_safe_eval_with_local_env(self):
        """Test safe_eval with local environment."""
        # Test with simple variables
        env = {"x": 10, "y": 20}
        self.assertEqual(safe_eval("x + y", env), 30)

        # Test with nested dict
        env = {"flags": {"under25": True, "student": False}}
        self.assertEqual(safe_eval("flags.under25", env), True)
        self.assertEqual(safe_eval("flags.student", env), False)

        # Test with mixed environment
        env = {"gross": 1000, "flags": {"under25": True}}
        self.assertEqual(safe_eval("gross * 0.1 * (flags.under25)", env), 100.0)

    def test_safe_eval_security_restrictions(self):
        """Test safe_eval security restrictions."""
        # Test with built-in functions that should be blocked
        with self.assertRaises(NameError):
            safe_eval("__import__('os')")

        # Test with exec
        with self.assertRaises(NameError):
            safe_eval("exec('print(1)')")

        # Test with eval
        with self.assertRaises(NameError):
            safe_eval("eval('1+1')")

        # Test with attribute access to built-ins
        with self.assertRaises(SafeEvalError):
            safe_eval("().__class__")

        # Test with syntax error
        with self.assertRaises(SafeEvalError):
            safe_eval("1 +")

    def test_compile_safe_expr_with_literals(self):
        """Test compile_safe_expr with literal values."""
        # Test with integer
        fn = compile_safe_expr(42)
        self.assertEqual(fn({}, {}), 42)

        # Test with float
        fn = compile_safe_expr(3.14)
        self.assertEqual(fn({}, {}), 3.14)

        # Test with boolean
        fn = compile_safe_expr(True)
        self.assertEqual(fn({}, {}), True)

    def test_compile_safe_expr_with_expressions(self):
        """Test compile_safe_expr with expressions."""
        # Test with simple expression
        fn = compile_safe_expr("2 + 3")
        self.assertEqual(fn({"gross": 0, "flags": {}}, {}), 5)

        # Test with gross reference
        fn = compile_safe_expr("gross * 0.1")
        self.assertEqual(fn({"gross": 1000, "flags": {}}, {}), 100.0)

        # Test with flags
        fn = compile_safe_expr("gross * 0.1 * (flags.under25)")
        self.assertEqual(fn({"gross": 1000, "flags": {"under25": True}}, {}), 100.0)
        self.assertEqual(fn({"gross": 1000, "flags": {"under25": False}}, {}), 0.0)

        # Test with results (previous rule amounts)
        fn = compile_safe_expr("rule1 * 0.5")
        self.assertEqual(fn({"gross": 1000, "flags": {}}, {"rule1": 200}), 100.0)

    def test_compile_safe_expr_with_constants(self):
        """Test compile_safe_expr with constants."""
        # Test with constants
        constants = {"TAX_RATE": 0.15, "MIN_WAGE": 1000}
        fn = compile_safe_expr("gross * TAX_RATE * (gross > MIN_WAGE)", constants)
        self.assertEqual(fn({"gross": 2000, "flags": {}}, {}), 300.0)
        self.assertEqual(fn({"gross": 500, "flags": {}}, {}), 0.0)

    def test_compile_safe_expr_docstring(self):
        """Test that compile_safe_expr stores the original expression in the docstring."""
        expr = "flags.under25 and gross < 1000"
        fn = compile_safe_expr(expr)
        self.assertEqual(fn.__doc__, expr)


if __name__ == "__main__":
    unittest.main()
