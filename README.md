# Hungarian Tax Calculator

A simplified tax calculator for Hungarian employee salaries that calculates net salary and employer costs based on various personal conditions and tax rules.

## Overview

This application provides a REST API for calculating payroll taxes in Hungary for the years 2024 and 2025. It uses a flexible rule-based system defined in JSONC files to determine tax calculations based on various personal conditions.

## Features

- Calculate net salary and employer costs based on gross salary
- Support for special tax conditions:
  - Mothers under 30 years old
  - Employees under 25 years old
  - Number of dependent children
  - First-time job entrants
  - Employment duration
- Detailed breakdown of all tax components
- API with Swagger documentation
- Docker support for easy deployment

## Installation

### Prerequisites

- Python 3.10+
- uv (Python package manager)

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hungarian-tax-calculator.git
   cd hungarian-tax-calculator
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the application:
   ```bash
   uv run src/tax_calculator/api.py
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

Once running, the API is available at http://localhost:8000 with the following endpoints:

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
  "year": 2024,
  "gross": 500000,
  "net": 332500,
  "super_gross": 565000,
  "flags": {
    "mother_under30": false,
    "under25": false,
    "children": 0,
    "entrant": false,
    "months_on_job": 12
  },
  "breakdown": {
    "tb_jarulek": {
      "label": "TB-járulék 18,5 %",
      "amount": -92500,
      "direction": "employee"
    },
    "szja_full": {
      "label": "SZJA 15 %",
      "amount": -75000,
      "direction": "employee"
    },
    "szocho_full": {
      "label": "SZOCHO 13 %",
      "amount": 65000,
      "direction": "employer"
    }
  }
}
```

## Documentation

API documentation is available at http://localhost:8000/docs when the server is running.

## Rule System

Tax rules are defined in JSONC files in the `dsl` directory:
- `dsl/hu2024.jsonc` - Rules for 2024
- `dsl/hu2025.jsonc` - Rules for 2025

The rule system supports:
- Percentage-based calculations
- Fixed credits
- Conditional rules based on personal circumstances

## License

[MIT License](LICENSE)
