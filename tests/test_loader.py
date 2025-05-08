"""Unit tests for the loader module."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.payroll_tax_calculator.loader import load_rules
from src.payroll_tax_calculator.rules import _RULE_REGISTRY, CompiledRule


class TestLoader(unittest.TestCase):
    """Test cases for the loader module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Sample DSL content in YAML format
        self.sample_dsl_yaml = """
        meta:
          country: TEST
          year: 2025
        variables:
          VAR1: 100
          VAR2: 200
        rules:
          - id: rule1
            type: percentage
            direction: employee
            rate: '0.1'
            base: gross
          - id: rule3
            type: credit
            amount: VAR1
        """

        # Create a temporary DSL file
        self.dsl_path = os.path.join(self.temp_dir.name, "test_dsl.yaml")
        with open(self.dsl_path, "w") as f:
            f.write(self.sample_dsl_yaml)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_load_rules_file_not_found(self):
        """Test load_rules with a non-existent file."""
        with self.assertRaises(FileNotFoundError):
            load_rules("non_existent_file.yaml")

    def test_load_rules_invalid_extension(self):
        """Test load_rules with an invalid file extension."""
        # Create a file with invalid extension
        invalid_ext_path = os.path.join(self.temp_dir.name, "invalid.json")
        with open(invalid_ext_path, "w") as f:
            f.write("{}")

        with self.assertRaises(ValueError) as context:
            load_rules(invalid_ext_path)

        self.assertIn("Unsupported file format", str(context.exception))

    def test_load_rules_invalid_yaml(self):
        """Test load_rules with invalid YAML."""
        # Create a file with invalid YAML
        invalid_yaml_path = os.path.join(self.temp_dir.name, "invalid.yaml")
        with open(invalid_yaml_path, "w") as f:
            f.write("invalid: yaml: content: - not properly formatted")

        with self.assertRaises(Exception):
            load_rules(invalid_yaml_path)

    @patch("src.payroll_tax_calculator.rules._RULE_REGISTRY")
    def test_load_rules_unknown_rule_type(self, mock_registry):
        """Test load_rules with an unknown rule type."""
        # Create a file with an unknown rule type
        unknown_rule_path = os.path.join(self.temp_dir.name, "unknown_rule.yaml")
        with open(unknown_rule_path, "w") as f:
            f.write("""
            rules:
              - id: rule1
                type: unknown_type
            """)

        # Mock the registry to not contain the unknown type
        mock_registry.__contains__.return_value = False

        with self.assertRaises(KeyError) as context:
            load_rules(unknown_rule_path)

        self.assertIn("Unknown rule type", str(context.exception))

    def test_load_rules_valid_file(self):
        """Test load_rules with a valid DSL file."""
        # Mock the rule registry and rule classes
        original_registry = dict(_RULE_REGISTRY)
        try:
            # Create mock rule classes
            percentage_rule = MagicMock()
            percentage_rule.compile.return_value = MagicMock(spec=CompiledRule)

            credit_rule = MagicMock()
            credit_rule.compile.return_value = MagicMock(spec=CompiledRule)

            # Update the registry with our mocks
            _RULE_REGISTRY.clear()
            _RULE_REGISTRY.update(
                {"percentage": percentage_rule, "credit": credit_rule}
            )

            # Load the rules
            compiled_rules, meta, variables = load_rules(self.dsl_path)

            # Check that the correct number of rules were compiled
            self.assertEqual(len(compiled_rules), 2)

            # Check that the meta data was loaded correctly
            self.assertEqual(meta["country"], "TEST")
            self.assertEqual(meta["year"], 2025)

            # Check that the variables were loaded correctly
            self.assertEqual(variables["VAR1"], 100)
            self.assertEqual(variables["VAR2"], 200)

            # Check that the rule compilation was called with correct arguments
            percentage_rule.compile.assert_called_once()
            credit_rule.compile.assert_called_once()

            # Verify the arguments passed to compile
            percentage_args = percentage_rule.compile.call_args[0]
            self.assertEqual(percentage_args[0]["id"], "rule1")
            self.assertEqual(percentage_args[0]["type"], "percentage")
            self.assertEqual(percentage_args[1], variables)

            credit_args = credit_rule.compile.call_args[0]
            self.assertEqual(credit_args[0]["id"], "rule3")
            self.assertEqual(credit_args[0]["type"], "credit")
            self.assertEqual(credit_args[1], variables)

        finally:
            # Restore the original registry
            _RULE_REGISTRY.clear()
            _RULE_REGISTRY.update(original_registry)

    def test_load_rules_with_path_object(self):
        """Test load_rules with a Path object instead of a string."""
        # Mock the rule registry and rule classes
        original_registry = dict(_RULE_REGISTRY)
        try:
            # Create mock rule classes
            percentage_rule = MagicMock()
            percentage_rule.compile.return_value = MagicMock(spec=CompiledRule)

            credit_rule = MagicMock()
            credit_rule.compile.return_value = MagicMock(spec=CompiledRule)

            # Update the registry with our mocks
            _RULE_REGISTRY.clear()
            _RULE_REGISTRY.update(
                {"percentage": percentage_rule, "credit": credit_rule}
            )

            # Load the rules using a Path object
            path_obj = Path(self.dsl_path)
            compiled_rules, meta, variables = load_rules(path_obj)

            # Check that the correct number of rules were compiled
            self.assertEqual(len(compiled_rules), 2)

        finally:
            # Restore the original registry
            _RULE_REGISTRY.clear()
            _RULE_REGISTRY.update(original_registry)


if __name__ == "__main__":
    unittest.main()
