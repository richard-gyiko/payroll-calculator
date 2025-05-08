# Payroll Tax Calculator

![Docker Image Version](https://img.shields.io/docker/v/gyikesz/payroll-tax-calculator)
[![codecov](https://codecov.io/gh/richard-gyiko/payroll-tax-calculator/graph/badge.svg?token=9HG1ZZGMML)](https://codecov.io/gh/richard-gyiko/payroll-tax-calculator)

A flexible, rule-based calculator for employee taxes that determines net salary and employer costs based on various personal conditions and tax rules.

## Overview

This application provides a REST API and MCP Server for calculating employment-related taxes and contributions using a flexible rule-based system defined in JSONC files. While it comes with Hungarian tax rules for 2024 and 2025, the engine is country-agnostic and can be extended with any valid DSL configuration.

## Features

- Calculate net salary and employer costs based on gross salary
- Rule-based engine with support for:
  - Percentage-based calculations
  - Fixed credits
  - Conditional rules based on personal circumstances
- Detailed breakdown of all tax components
- Dual integration options:
  - REST API with Swagger documentation
  - MCP server for AI agent integration
- Docker support for easy deployment
- DSL validation tool for ensuring rule files are correctly formatted

## Installation

### Prerequisites

- Python 3.10+
- uv (Python package manager)

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/richard-gyiko/payroll-tax-calculator
   cd payroll-tax-calculator
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the application:
   ```bash
   uv run src/payroll_calculator/api.py
   ```

### Docker Setup

1. Pull the Docker image directly from DockerHub:
   ```bash
   docker pull gyikesz/payroll-tax-calculator
   ```

   Or build the Docker image locally:
   ```bash
   docker build -t payroll-tax-calculator .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 gyikesz/payroll-tax-calculator
   ```

## API Usage

This application provides two interfaces:

1. **REST API**: Available at http://localhost:8000
2. **MCP Server**: Available at http://localhost:8000/mcp

### REST API

### Calculate Payroll

**Endpoint:** `POST /calculate`

**Request Body:**
```json
{
  "year": 2024,
  "gross": 500000,
  "mother_under30": false,
  "under25": false,
  "children": 0,
  "entrant": false,
  "months_on_job": 12
}
```

**Response:**
```json
{
  "year": 2025,
  "gross": 480000,
  "net": 391200,
  "super_gross": 504596,
  "flags": {
    "mother_under30": false,
    "under25": true,
    "children": 0,
    "entrant": true,
    "months_on_job": 6
  },
  "breakdown": {
    "tb_jarulek": {
      "label": "TB-járulék 18,5 %",
      "amount": -88800,
      "direction": "employee"
    },
    "szja_full": {
      "label": "SZJA 15 %",
      "amount": -72000,
      "direction": "employee"
    },
    "under25_credit": {
      "label": "25 év alatti SZJA-jóváírás",
      "amount": 72000,
      "direction": "employee"
    },
    "szocho_full": {
      "label": "SZOCHO 13 %",
      "amount": 62400,
      "direction": "employer"
    },
    "entrant_full_credit": {
      "label": "SZOCHO-kedvezmény 0 % (minimálbérig, 1-12. hó)",
      "amount": -37804,
      "direction": "employer"
    }
  }
}
```

### MCP Server

The application also exposes an MCP (Model Context Protocol) server at http://localhost:8000/mcp. This allows AI agents to interact with the tax calculator directly.

MCP is an emerging standard that defines how AI agents communicate with applications. The MCP server exposes the same functionality as the REST API but in a format that can be consumed by AI assistants and tools that support the MCP protocol.

To connect an MCP client to the server:

```json
{
  "mcpServers": {
    "payroll-tax-calculator": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

For clients that don't support SSE or if you need authentication, you can use mcp-remote as a bridge:

```json
{
  "mcpServers": {
    "payroll-tax-calculator": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8000/mcp",
        "8080"
      ]
    }
  }
}
```

## Documentation

API documentation is available at http://localhost:8000/docs when the server is running.

## Testing

The project includes a comprehensive test suite to ensure reliability and correctness.

### Test Structure

- `test_engine.py`: Tests for the `PayrollEngine` class
- `test_loader.py`: Tests for the DSL file loading functionality
- `test_safe_eval.py`: Tests for the safe expression evaluation module
- `test_integration.py`: Integration tests that verify the components working together
- `conftest.py`: Common pytest fixtures used across test files
- `data/`: Directory containing test data files

### Running Tests Locally

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

### Test Coverage

The tests aim to cover:

1. Normal operation scenarios
2. Edge cases
3. Error handling
4. Security restrictions (especially for safe_eval)

### Test Dependencies

The test suite requires the following dependencies, which are included in the dev dependencies:

```bash
uv sync --dev
```

This will install:
- pytest: Testing framework
- pytest-cov: Coverage reporting

For more detailed information about testing, see the [Tests README](tests/README.md).

## Rule System

The calculator uses a flexible Domain-Specific Language (DSL) to define tax rules. The engine is country-agnostic and can work with any valid rule configuration.

Currently implemented rule sets:
- [Hungarian Rules 2024](dsl/hu2024/README.md)
- [Hungarian Rules 2025](dsl/hu2025/README.md)

For detailed information about the rule system and how to extend it, see the [DSL documentation](dsl/README.md).

### Validating DSL Files

The package includes a validation tool to check DSL files against the schema:

```bash
uv run src/payroll_tax_calculator/validate.py dsl/hu2024 dsl/hu2025
```

This ensures your rule files are correctly formatted before using them with the calculator.

## License

[MIT License](LICENSE)
