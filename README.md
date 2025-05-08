# Payroll Tax Calculator

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

## Installation

### Prerequisites

- Python 3.10+
- uv (Python package manager)

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/payroll-tax-calculator.git
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

1. Build the Docker image:
   ```bash
   docker build -t tax-calculator .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 tax-calculator
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

## Rule System

The calculator uses a flexible Domain-Specific Language (DSL) to define tax rules. The engine is country-agnostic and can work with any valid rule configuration.

Currently implemented rule sets:
- [Hungarian Rules 2024](dsl/hu2024/README.md)
- [Hungarian Rules 2025](dsl/hu2025/README.md)

For detailed information about the rule system and how to extend it, see the [DSL documentation](dsl/README.md).

## License

[MIT License](LICENSE)
