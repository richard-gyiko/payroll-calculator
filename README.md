# Payroll Tax Calculator

![Docker Image Version](https://img.shields.io/docker/v/gyikesz/payroll-tax-calculator)
[![codecov](https://codecov.io/gh/richard-gyiko/payroll-tax-calculator/graph/badge.svg?token=9HG1ZZGMML)](https://codecov.io/gh/richard-gyiko/payroll-tax-calculator)

> **A flexible, rule-based calculator that simplifies payroll tax calculations, accurately determining net salary and employer costs based on various personal conditions and tax rules.**

---

## 📑 Table of Contents

- [Overview](#overview)
- [✨ Key Features](#-key-features)
- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Setup](#local-setup)
  - [Docker Setup](#docker-setup)
- [🔌 API Usage](#-api-usage)
  - [REST API](#rest-api)
  - [MCP Server](#mcp-server)
- [📚 Documentation](#-documentation)
- [🧪 Testing](#-testing)
- [📏 Rule System](#-rule-system)
- [📄 License](#-license)

---

## Overview

This application provides a powerful and flexible system for calculating employment-related taxes and contributions. Using a rule-based engine defined in YAML files, it can handle complex tax calculations for different scenarios and jurisdictions.

While it comes pre-configured with Hungarian tax rules for 2024 and 2025, the engine is **completely country-agnostic** and can be extended with any valid DSL configuration to support tax rules from any country or region.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 💰 **Accurate Calculations** | Calculate net salary and employer costs based on gross salary with precision |
| 🧩 **Flexible Rule Engine** | Support for percentage-based calculations, fixed credits, and conditional rules |
| 📊 **Detailed Breakdown** | Get comprehensive breakdown of all tax components for transparency |
| 🔄 **Dual Integration** | Choose between REST API or MCP server for AI agent integration |
| 🐳 **Docker Support** | Easy deployment with Docker containers |
| ✅ **DSL Validation** | Built-in tools to ensure rule files are correctly formatted |
| 🌍 **Country Agnostic** | Adaptable to any country's tax rules with the right configuration |

---

## 🚀 Getting Started

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
   uv run src/payroll_tax_calculator/api.py
   ```

### Docker Setup

**Option 1:** Pull the Docker image directly from DockerHub:
```bash
docker pull gyikesz/payroll-tax-calculator
```

**Option 2:** Build the Docker image locally:
```bash
docker build -t payroll-tax-calculator .
```

Run the container:
```bash
docker run -p 8000:8000 gyikesz/payroll-tax-calculator
```

---

## 🔌 API Usage

This application provides two powerful interfaces:

### REST API

Access the REST API at: **http://localhost:8000**

#### Calculate Payroll Example

**Endpoint:** `POST /calculate`

**Request Body:**
```json
{
  "country": "hu",
  "date": "2024-01-01",
  "gross": 500000,
  "flags": {
    "mother_under30": false,
    "under25": false,
    "children": 0,
    "entrant": false,
    "months_on_job": 12
  }
}
```

**Response:**
```json
{
  "date": "2024-01-01",
  "gross": 500000,
  "net": 332500,
  "super_gross": 565000,
  "breakdown": {
    "tb_jarulek": {
      "label": "TB-járulék 18,5 %",
      "amount": -92500.0,
      "direction": "employee"
    },
    "szja_full": {
      "label": "SZJA 15 %",
      "amount": -75000.0,
      "direction": "employee"
    },
    "szocho_full": {
      "label": "SZOCHO 13 %",
      "amount": 65000.0,
      "direction": "employer"
    }
  }
}
```

### MCP Server

The application also exposes an MCP (Model Context Protocol) server at **http://localhost:8000/mcp**. This allows AI agents to interact with the tax calculator directly.

MCP is an emerging standard that defines how AI agents communicate with applications. The MCP server exposes the same functionality as the REST API but in a format that can be consumed by AI assistants and tools that support the MCP protocol.

#### Connecting an MCP Client

**Standard Connection:**
```json
{
  "mcpServers": {
    "payroll-tax-calculator": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Using mcp-remote as a bridge** (for clients that don't support SSE or if you need authentication):
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

---

## 📚 Documentation

API documentation with interactive Swagger UI is available at **http://localhost:8000/docs** when the server is running.

---

## 🧪 Testing

The project includes a comprehensive test suite to ensure reliability and correctness.

### Test Structure

| Test File | Purpose |
|-----------|---------|
| `test_engine.py` | Tests for the `PayrollEngine` class |
| `test_loader.py` | Tests for the DSL file loading functionality |
| `test_safe_eval.py` | Tests for the safe expression evaluation module |
| `test_integration.py` | Integration tests that verify the components working together |
| `conftest.py` | Common pytest fixtures used across test files |
| `data/` | Directory containing test data files |

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=src/payroll_tax_calculator --cov-report=term-missing

# Run a specific test file
pytest tests/test_engine.py
```

### Test Coverage

The tests aim to cover:
1. ✅ Normal operation scenarios
2. ✅ Edge cases
3. ✅ Error handling
4. ✅ Security restrictions (especially for safe_eval)

### Test Dependencies

The test suite requires the following dependencies, which are included in the dev dependencies:

```bash
uv sync --dev
```

This will install:
- pytest: Testing framework
- pytest-cov: Coverage reporting

For more detailed information about testing, see the [Tests README](tests/README.md).

---

## 📏 Rule System

The calculator uses a flexible Domain-Specific Language (DSL) to define tax rules. The engine is country-agnostic and can work with any valid rule configuration.

### Currently Implemented Rule Sets

- 🇭🇺 [Hungarian Rules 2024](dsl/hu2024/dsl.yaml)
- 🇭🇺 [Hungarian Rules 2025](dsl/hu2025/dsl.yaml)

For detailed information about the rule system and how to extend it, see the [DSL documentation](dsl/README.md).

### Validating DSL Files

The package includes a validation tool to check DSL files against the schema:

```bash
uv run src/payroll_tax_calculator/validate.py dsl/hu2024 dsl/hu2025
```

This ensures your rule files are correctly formatted before using them with the calculator.

---

## 📄 License

[MIT License](LICENSE)
