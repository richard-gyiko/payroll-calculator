"""Pytest configuration and fixtures for the payroll tax calculator tests."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.payroll_tax_calculator.rules import CompiledRule


@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def test_dsl_path(test_data_dir):
    """Return the path to the test DSL file."""
    return test_data_dir / "test_dsl.jsonc"


@pytest.fixture
def mock_compiled_rules():
    """Return a list of mock CompiledRule objects for testing."""
    rule1 = MagicMock(spec=CompiledRule)
    rule1.id = "income_tax"
    rule1.label = "Income Tax 15%"
    rule1.direction = "employee"
    rule1.amount.return_value = -150.0  # 15% of 1000

    rule2 = MagicMock(spec=CompiledRule)
    rule2.id = "tax_credit"
    rule2.label = "Tax Credit for Low Income"
    rule2.direction = "employee"
    rule2.amount.return_value = 100.0  # 10% of MIN_WAGE (1000)

    rule3 = MagicMock(spec=CompiledRule)
    rule3.id = "employer_contribution"
    rule3.label = "Employer Social Contribution"
    rule3.direction = "employer"
    rule3.amount.return_value = 200.0  # 20% of 1000

    return [rule1, rule2, rule3]


@pytest.fixture
def sample_context():
    """Return a sample context dictionary for testing."""
    return {"gross": 1000, "flags": {"under25": True, "student": False, "children": 2}}


@pytest.fixture
def sample_breakdown():
    """Return a sample breakdown dictionary for testing."""
    return {
        "income_tax": {
            "label": "Income Tax 15%",
            "amount": -150.0,
            "direction": "employee",
        },
        "tax_credit": {
            "label": "Tax Credit for Low Income",
            "amount": 100.0,
            "direction": "employee",
        },
    }
