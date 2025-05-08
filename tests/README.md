# Payroll Tax Calculator Tests

This directory contains unit and integration tests for the Payroll Tax Calculator.

## Test Structure

- `test_engine.py`: Tests for the `PayrollEngine` class
- `test_loader.py`: Tests for the DSL file loading functionality
- `test_safe_eval.py`: Tests for the safe expression evaluation module
- `test_integration.py`: Integration tests that verify the components working together
- `conftest.py`: Common pytest fixtures used across test files
- `data/`: Directory containing test data files

## Running Tests

To run all tests:

```bash
pytest
```

To run tests with coverage report:

```bash
pytest --cov=src/payroll_tax_calculator --cov-report=term-missing
```

To run a specific test file:

```bash
pytest tests/test_engine.py
```

To run a specific test:

```bash
pytest tests/test_engine.py::TestPayrollEngine::test_run_with_rules
```

## Test Data

The `data/` directory contains sample DSL files used for testing. These files follow the same format as the production DSL files but are simplified for testing purposes.

## Test Coverage

The tests aim to cover:

1. Normal operation scenarios
2. Edge cases
3. Error handling
4. Security restrictions (especially for safe_eval)

## Adding New Tests

When adding new tests:

1. Follow the existing naming conventions
2. Add docstrings explaining the purpose of each test
3. Use the fixtures defined in `conftest.py` where appropriate
4. Ensure tests are independent and don't rely on external resources
5. For new components, create a dedicated test file

## Mocking

The tests use Python's `unittest.mock` module to isolate components during testing. This allows testing components independently without relying on the correct functioning of other components.