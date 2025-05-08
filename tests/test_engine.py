"""Unit tests for the engine module."""

import unittest
from unittest.mock import patch, MagicMock

from src.payroll_tax_calculator.engine import PayrollEngine
from src.payroll_tax_calculator.rules import CompiledRule


class TestPayrollEngine(unittest.TestCase):
    """Test cases for the PayrollEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock rules for testing
        self.rule1 = MagicMock(spec=CompiledRule)
        self.rule1.id = "rule1"
        self.rule1.label = "Rule 1"
        self.rule1.direction = "employee"
        self.rule1.amount.return_value = -100.0

        self.rule2 = MagicMock(spec=CompiledRule)
        self.rule2.id = "rule2"
        self.rule2.label = "Rule 2"
        self.rule2.direction = "employer"
        self.rule2.amount.return_value = 200.0

        self.rule3 = MagicMock(spec=CompiledRule)
        self.rule3.id = "rule3"
        self.rule3.label = "Rule 3"
        self.rule3.direction = "employee"
        self.rule3.amount.return_value = 0.0  # This rule doesn't apply (returns 0)

        # Create engine with mock rules
        self.engine = PayrollEngine([self.rule1, self.rule2, self.rule3])

    def test_init(self):
        """Test PayrollEngine initialization."""
        self.assertEqual(len(self.engine.rules), 3)
        self.assertEqual(self.engine.rules[0].id, "rule1")
        self.assertEqual(self.engine.rules[1].id, "rule2")
        self.assertEqual(self.engine.rules[2].id, "rule3")

    @patch('src.payroll_tax_calculator.engine.load_rules')
    def test_from_json(self, mock_load_rules):
        """Test PayrollEngine.from_json factory method."""
        # Setup mock
        mock_rules = [MagicMock(spec=CompiledRule)]
        mock_load_rules.return_value = (mock_rules, {}, {})

        # Call method
        engine = PayrollEngine.from_json("dummy/path.json")

        # Assertions
        mock_load_rules.assert_called_once_with("dummy/path.json")
        self.assertEqual(engine.rules, mock_rules)

    def test_run_with_rules(self):
        """Test PayrollEngine.run with multiple rules."""
        # Run the engine with a gross salary and some flags
        result = self.engine.run(1000, flag1=True, flag2=False)

        # Check that rules were called with correct context
        expected_ctx = {"gross": 1000, "flags": {"flag1": True, "flag2": False}}
        self.rule1.amount.assert_called_once()
        ctx_arg = self.rule1.amount.call_args[0][0]
        self.assertEqual(ctx_arg["gross"], expected_ctx["gross"])
        self.assertEqual(ctx_arg["flags"], expected_ctx["flags"])

        # Check the result structure
        self.assertEqual(result["gross"], 1000)
        self.assertEqual(result["net"], 900)  # 1000 - 100 (rule1)
        self.assertEqual(result["super_gross"], 1200)  # 1000 + 200 (rule2)
        
        # Check breakdown
        self.assertEqual(len(result["breakdown"]), 2)  # rule3 returns 0, so not included
        self.assertEqual(result["breakdown"]["rule1"]["amount"], -100.0)
        self.assertEqual(result["breakdown"]["rule1"]["direction"], "employee")
        self.assertEqual(result["breakdown"]["rule2"]["amount"], 200.0)
        self.assertEqual(result["breakdown"]["rule2"]["direction"], "employer")

    def test_run_with_empty_rules(self):
        """Test PayrollEngine.run with no rules."""
        engine = PayrollEngine([])
        result = engine.run(1000)
        
        # With no rules, net should equal gross and super_gross should equal gross
        self.assertEqual(result["gross"], 1000)
        self.assertEqual(result["net"], 1000)
        self.assertEqual(result["super_gross"], 1000)
        self.assertEqual(result["breakdown"], {})

    def test_get_flags(self):
        """Test PayrollEngine.get_flags method."""
        # Create mock rules with docstrings containing flag references
        rule1 = MagicMock(spec=CompiledRule)
        rule1.condition_fn = MagicMock()
        rule1.condition_fn.__doc__ = "flags.under25 and flags.student"
        rule1.amount_fn = MagicMock()
        rule1.amount_fn.__doc__ = None

        rule2 = MagicMock(spec=CompiledRule)
        rule2.condition_fn = MagicMock()
        rule2.condition_fn.__doc__ = None
        rule2.amount_fn = MagicMock()
        rule2.amount_fn.__doc__ = "flags.children * 10"

        rule3 = MagicMock(spec=CompiledRule)
        rule3.condition_fn = MagicMock()
        rule3.condition_fn.__doc__ = "flags.mother_under30"
        rule3.amount_fn = MagicMock()
        rule3.amount_fn.__doc__ = "flags.months_on_job < 12"

        engine = PayrollEngine([rule1, rule2, rule3])
        flags = engine.get_flags()

        # Check that all flags were extracted and sorted
        self.assertEqual(flags, ["children", "months_on_job", "mother_under30", "student", "under25"])

    def test_extract_flags_from_docstring(self):
        """Test _extract_flags_from_docstring static method."""
        docstring = "This is a test with flags.flag1 and flags.flag2 and flags.complex_flag_name"
        flags = PayrollEngine._extract_flags_from_docstring(docstring)
        self.assertEqual(flags, {"flag1", "flag2", "complex_flag_name"})

        # Test with no flags
        docstring = "This is a test with no flags"
        flags = PayrollEngine._extract_flags_from_docstring(docstring)
        self.assertEqual(flags, set())

        # Test with flags followed by operators
        docstring = "flags.flag1 + flags.flag2 * flags.flag3"
        flags = PayrollEngine._extract_flags_from_docstring(docstring)
        self.assertEqual(flags, {"flag1", "flag2", "flag3"})


if __name__ == "__main__":
    unittest.main()