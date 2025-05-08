"""Integration tests for the payroll tax calculator."""

import pytest

from src.payroll_tax_calculator.engine import PayrollEngine
from src.payroll_tax_calculator.loader import load_rules


class TestIntegration:
    """Integration tests for the payroll tax calculator."""

    def test_end_to_end_calculation(self, test_dsl_path):
        """Test the end-to-end calculation process using a test DSL file."""
        # Load rules from the test DSL file
        engine = PayrollEngine.from_json(test_dsl_path)
        
        # Run the engine with a gross salary
        result = engine.run(1000)
        
        # Check the result structure
        assert result["gross"] == 1000
        assert "net" in result
        assert "super_gross" in result
        assert "breakdown" in result
        
        # Check that all rules were applied
        breakdown = result["breakdown"]
        assert "income_tax" in breakdown
        assert "tax_credit" in breakdown
        assert "employer_contribution" in breakdown
        
        # Check the calculations
        assert breakdown["income_tax"]["amount"] == -150.0  # 15% of 1000
        assert breakdown["tax_credit"]["amount"] == 100.0  # 10% of MIN_WAGE (1000)
        assert breakdown["employer_contribution"]["amount"] == 200.0  # 20% of 1000
        
        # Check the totals
        assert result["net"] == 950.0  # 1000 - 150 + 100
        assert result["super_gross"] == 1200.0  # 1000 + 200

    def test_end_to_end_with_flags(self, test_dsl_path):
        """Test the end-to-end calculation with flags."""
        engine = PayrollEngine.from_json(test_dsl_path)
        
        # Run with a high gross salary (above the tax credit threshold)
        result = engine.run(3000)
        
        # Tax credit should not be applied (condition: gross < MIN_WAGE * 2)
        assert "tax_credit" not in result["breakdown"]
        
        # Check the totals
        assert result["net"] == 2550.0  # 3000 - 450 (15% of 3000)
        assert result["super_gross"] == 3600.0  # 3000 + 600 (20% of 3000)

    def test_get_flags_from_dsl(self, test_dsl_path):
        """Test extracting flags from the DSL file."""
        engine = PayrollEngine.from_json(test_dsl_path)
        
        # The test DSL doesn't have any flags in the conditions,
        # so we'll modify one of the rules to use flags
        rule = engine.rules[1]  # tax_credit rule
        rule.condition_fn.__doc__ = "flags.under25 and gross < MIN_WAGE * 2"
        
        flags = engine.get_flags()
        assert "under25" in flags

    def test_load_and_run_with_variables(self, test_dsl_path):
        """Test loading rules with variables and running the engine."""
        # Load rules directly to access variables
        compiled_rules, meta, variables = load_rules(test_dsl_path)
        
        # Check that variables were loaded correctly
        assert variables["TAX_RATE"] == 0.15
        assert variables["MIN_WAGE"] == 1000
        assert variables["MAX_DEDUCTION"] == 500
        
        # Create engine and run
        engine = PayrollEngine(compiled_rules)
        result = engine.run(variables["MIN_WAGE"])
        
        # Check that variables were used in calculations
        assert result["breakdown"]["income_tax"]["amount"] == -variables["MIN_WAGE"] * variables["TAX_RATE"]
        assert result["breakdown"]["tax_credit"]["amount"] == variables["MIN_WAGE"] * 0.1

    def test_rule_conditions(self, test_dsl_path):
        """Test that rule conditions are properly evaluated."""
        engine = PayrollEngine.from_json(test_dsl_path)
        
        # Run with different gross values to test the tax_credit condition
        result1 = engine.run(1000)  # Below threshold, should get credit
        result2 = engine.run(2500)  # Above threshold, should not get credit
        
        assert "tax_credit" in result1["breakdown"]
        assert "tax_credit" not in result2["breakdown"]


if __name__ == "__main__":
    pytest.main()