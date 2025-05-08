# Payroll Tax Calculator DSL

The Payroll Tax Calculator uses a flexible Domain-Specific Language (DSL) defined in JSONC files to specify tax rules. This approach allows for transparent, auditable calculations and easy extension to support new tax rules or jurisdictions.

## Available Rule Sets

The calculator comes with the following rule sets:

- [Hungarian Rules 2024](hu2024/dsl.jsonc) - Payroll Tax rules for Hungary effective from January 1, 2024 (subset of the full 2024 rules)
- [Hungarian Rules 2025](hu2025/dsl.jsonc) - Payroll Tax rules for Hungary effective from January 1, 2025 (subset of the full 2025 rules)

Please note that the rules are not yet finalized and may change.

## DSL Structure

Each rule file has the following structure:

```json
{
  "meta": {
    "country": "XX",
    "year": 2024,
    "description": "Description of the rule set"
  },
  "variables": {
    "VARIABLE_NAME": value
  },
  "rules": [
    {
      "id": "rule_id",
      "label": "Human-readable label",
      "type": "percentage|credit",
      "direction": "employee|employer",
      // Additional properties based on rule type
    }
  ]
}
```

## Rule Types

The DSL supports two main types of rules:

### Percentage Rule

Calculates a percentage of a base value, with a specified direction (employee or employer).

```json
{
  "id": "income_tax",
  "label": "Income Tax 15%",
  "type": "percentage",
  "direction": "employee",
  "rate": "TAX_RATE",
  "base": "gross"
}
```

### Credit Rule

Applies a fixed amount or calculated value as a credit or deduction.

```json
{
  "id": "tax_credit",
  "label": "Tax Credit",
  "type": "credit",
  "direction": "employee",
  "amount": "credit_formula",
  "condition": "optional_condition"
}
```

## Creating New Rule Sets

To create a new rule set:

1. Create a new directory for your country/year
2. Add a `dsl.jsonc` file with your rules

For more complex extensions, you can add new rule types by extending the `RuleType` class in the `rules.py` file.
