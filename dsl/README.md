# Payroll Tax Calculator DSL

The Payroll Tax Calculator uses a flexible Domain-Specific Language (DSL) to specify tax rules. The DSL uses YAML format, allowing for transparent, auditable calculations and easy extension to support new tax rules or jurisdictions.

## Table of Contents

- [Introduction](#introduction)
- [Available Rule Sets](#available-rule-sets)
- [DSL Structure](#dsl-structure)
  - [Meta Section](#meta-section)
  - [Variables Section](#variables-section)
  - [Rules Section](#rules-section)
- [Rule Types](#rule-types)
  - [Percentage Rule](#percentage-rule)
  - [Credit Rule](#credit-rule)
- [Variables](#variables)
- [Formulas and Expressions](#formulas-and-expressions)
  - [Mathematical Operations](#mathematical-operations)
  - [Available Functions](#available-functions)
  - [Value References](#value-references)
- [Conditions](#conditions)
  - [Comparison Operators](#comparison-operators)
  - [Logical Operators](#logical-operators)
  - [Flag References](#flag-references)
- [Flags](#flags)
- [Creating New Rule Sets](#creating-new-rule-sets)
  - [Step-by-Step Guide](#step-by-step-guide)
- [Troubleshooting](#troubleshooting)

## Introduction

The Payroll Tax Calculator DSL (Domain-Specific Language) is designed to express tax rules in a clear, maintainable, and auditable format. By using a DSL, we achieve several benefits:

1. **Transparency**: Tax rules are expressed in a human-readable format that can be reviewed by both technical and non-technical stakeholders
2. **Auditability**: Changes to tax rules can be tracked through version control
3. **Flexibility**: New tax rules or jurisdictions can be added without changing the core calculation engine
4. **Maintainability**: Rules are separated from the application code, making updates easier

The DSL is implemented in YAML, which provides a good balance between human readability and machine parseability. The calculation engine interprets these rules to compute payroll taxes based on various inputs like gross salary and employee characteristics.

## Available Rule Sets

The calculator comes with the following rule sets:

- [Hungarian Rules 2024](hu2024/dsl.yaml) - Payroll Tax rules for Hungary effective from January 1, 2024 (subset of the full 2024 rules)
- [Hungarian Rules 2025](hu2025/dsl.yaml) - Payroll Tax rules for Hungary effective from January 1, 2025 (subset of the full 2025 rules)

Please note that the rules are not yet finalized and may change.

## DSL Structure

Each rule file has the following structure:

```yaml
meta:
  country: XX
  year: 2024
  description: Description of the rule set

variables:
  VARIABLE_NAME: value

rules:
  - id: rule_id
    label: Human-readable label
    type: percentage|credit
    direction: employee|employer
    # Additional properties based on rule type
```

### Meta Section

The `meta` section contains metadata about the rule set:

- `country`: Two-letter country code (ISO 3166-1 alpha-2)
- `year`: The year for which the rules apply
- `description`: A human-readable description of the rule set

Example:

```yaml
meta:
  country: HU
  year: 2024
  description: 2024. január 1-től érvényes jogszabályok (25 év alatti, 30 év alatti anyák, családi kedvezmény, munkaerő-piacra lépő SZOCHO-kedvezmény)
```

### Variables Section

The `variables` section defines constants that can be referenced in rules. This makes the rules more readable and easier to maintain, as common values only need to be updated in one place.

Variables are defined as key-value pairs, where the key is the variable name (conventionally in UPPERCASE) and the value is a number.

Example:

```yaml
variables:
  # Minimálbér és garantált bérminimum – 639/2024. (XI.22.) Korm. rendelet
  MIN_WAGE: 266800 # havi minimálbér (Ft)
  GUAR_MIN_WAGE: 326000 # havi garantált bérminimum (Ft)
  
  # Adó- és járulékkulcsok (%)
  SZJA_RATE: 0.15 # személyi jövedelemadó
  SSC_RATE: 0.185 # TB járulék a munkavállalótól
```

### Rules Section

The `rules` section contains an array of rule definitions. Each rule has a specific type and properties that determine how it affects the calculation.

Common properties for all rules:

- `id`: A unique identifier for the rule (used in the calculation result)
- `label`: A human-readable label for the rule (displayed to users)
- `type`: The type of rule (`percentage` or `credit`)
- `direction`: Who pays/receives the amount (`employee`, `employer`, or `neutral`)
- `condition`: (Optional) An expression that determines if the rule applies

Additional properties depend on the rule type and are explained in the [Rule Types](#rule-types) section.

## Rule Types

The DSL supports two main types of rules:

### Percentage Rule

Calculates a percentage of a base value, with a specified direction (employee or employer).

Properties:

- `rate`: The percentage rate (can be a variable or a formula)
- `base`: The base value to apply the rate to (defaults to `gross` if not specified)

Example:

```yaml
- id: tb_jarulek
  label: TB-járulék 18,5 %
  type: percentage
  direction: employee
  rate: SSC_RATE
  base: gross
```

In this example, the rule calculates 18.5% of the gross salary as a social security contribution from the employee. The negative sign is automatically applied for employee-direction rules.

Another example with a condition:

```yaml
- id: reduced_tax
  label: Reduced Tax Rate
  type: percentage
  direction: employee
  rate: REDUCED_RATE
  base: gross
  condition: flags.eligible_for_reduction
```

### Credit Rule

Applies a fixed amount or calculated value as a credit or deduction.

Properties:

- `amount`: The amount of the credit (can be a variable, a fixed value, or a formula)
- `condition`: (Optional) An expression that determines if the credit applies

Example:

```yaml
- id: under25_credit
  label: 25 év alatti SZJA-jóváírás
  type: credit
  direction: employee
  amount: min(gross, UNDER25_CAP) * SZJA_RATE
  condition: flags.under25 and not flags.mother_under30
```

In this example, the rule provides a tax credit for employees under 25 years old. The credit amount is calculated as the income tax on the lesser of the gross salary or a cap value.

Another example with a negative amount (representing a deduction):

```yaml
- id: entrant_full_credit
  label: SZOCHO-kedvezmény 0 % (minimálbérig, 1-12. hó)
  type: credit
  direction: employer
  amount: -min(gross, MIN_WAGE) * SZOCHO_RATE
  condition: flags.entrant and flags.months_on_job < 12
```

## Variables

Variables are constants defined in the `variables` section of the DSL file. They serve several purposes:

1. Making rules more readable by using descriptive names instead of magic numbers
2. Centralizing values that may be used in multiple rules
3. Making it easier to update values when tax rates or thresholds change

### Variable Naming Conventions

- Use UPPERCASE for variable names
- Use underscores to separate words
- Use descriptive names that indicate what the variable represents

### Examples of Common Variables

- Tax rates: `SZJA_RATE`, `SSC_RATE`, `SZOCHO_RATE`
- Thresholds: `MIN_WAGE`, `GUAR_MIN_WAGE`, `UNDER25_CAP`
- Allowances: `FAM_ONE`, `FAM_TWO`, `FAM_THREE`

### Using Variables in Rules

Variables can be used in any formula within rules. They are referenced by their name:

```yaml
- id: income_tax
  label: Income Tax 15%
  type: percentage
  direction: employee
  rate: SZJA_RATE
  base: gross
```

## Formulas and Expressions

The DSL supports a variety of mathematical operations, functions, and value references in formulas.

### Mathematical Operations

The following mathematical operations are supported:

- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Floor Division: `//`
- Modulo: `%`
- Power: `**`

Example:

```yaml
amount: (gross * 0.5) + (MIN_WAGE * 0.1)
```

### Available Functions

The following functions are available for use in formulas:

- `abs(x)`: Absolute value of x
- `ceil(x)`: Ceiling of x (smallest integer greater than or equal to x)
- `floor(x)`: Floor of x (largest integer less than or equal to x)
- `round(x)`: Round x to the nearest integer
- `sqrt(x)`: Square root of x
- `min(x, y, ...)`: Minimum of the given values
- `max(x, y, ...)`: Maximum of the given values

Example:

```yaml
amount: min(gross, UNDER25_CAP) * SZJA_RATE
```

### Value References

Formulas can reference the following values:

- `gross`: The gross salary
- `flags.X`: Flag values (see [Flags](#flags) section)
- Rule IDs: Reference the amount calculated by a previous rule

Example:

```yaml
amount: gross - tb_jarulek - szja_full
```

## Conditions

Conditions are boolean expressions that determine whether a rule applies. They are evaluated at runtime based on the input data.

### Comparison Operators

The following comparison operators are supported:

- Equal: `==`
- Not Equal: `!=`
- Greater Than: `>`
- Greater Than or Equal: `>=`
- Less Than: `<`
- Less Than or Equal: `<=`

Example:

```yaml
condition: flags.months_on_job < 12
```

### Logical Operators

The following logical operators are supported:

- And: `and`
- Or: `or`
- Not: `not`

Example:

```yaml
condition: flags.under25 and not flags.mother_under30
```

### Flag References

Conditions often reference flags, which are boolean or numeric values provided as input to the calculation. Flags are accessed using the `flags.` prefix.

Example:

```yaml
condition: flags.children >= 3 and flags.date >= '2025-07-01'
```

## Flags

Flags are input parameters that can affect which rules apply and how they are calculated. They represent characteristics of the employee or the calculation context.

### Common Flags

Based on the existing rule sets, the following flags are commonly used:

- `under25`: Boolean indicating if the employee is under 25 years old
- `mother_under30`: Boolean indicating if the employee is a mother under 30 years old
- `children`: Integer indicating the number of children
- `entrant`: Boolean indicating if the employee is new to the job market
- `months_on_job`: Integer indicating how many months the employee has been on the job
- `date`: Date of the calculation (used for time-dependent rules)

### Using Flags in Rules

Flags can be used in both conditions and amount calculations:

```yaml
# In a condition
condition: flags.under25 and not flags.mother_under30

# In an amount calculation
amount: ((flags.children==1)*FAM_ONE + (flags.children==2)*FAM_TWO + (flags.children>=3)*FAM_THREE) * SZJA_RATE
```

## Creating New Rule Sets

To create a new rule set for a different country or year:

### Step-by-Step Guide

1. **Create a new directory** for your country/year:
   ```
   mkdir -p dsl/XX2024/
   ```
   Replace `XX` with your country code.

2. **Create a new `dsl.yaml` file** in the directory:
   ```
   touch dsl/XX2024/dsl.yaml
   ```

3. **Define the meta section**:
   ```yaml
   meta:
     country: XX
     year: 2024
     description: Tax rules for Country XX effective from January 1, 2024
   ```

4. **Define variables** for tax rates, thresholds, etc.:
   ```yaml
   variables:
     INCOME_TAX_RATE: 0.20
     SOCIAL_SECURITY_RATE: 0.10
     EMPLOYER_CONTRIBUTION_RATE: 0.15
     TAX_FREE_THRESHOLD: 10000
   ```

5. **Define rules** for the tax calculation:
   ```yaml
   rules:
     # Employee-side deductions
     - id: social_security
       label: Social Security Contribution
       type: percentage
       direction: employee
       rate: SOCIAL_SECURITY_RATE
       base: gross
     
     - id: income_tax
       label: Income Tax
       type: percentage
       direction: employee
       rate: INCOME_TAX_RATE
       base: gross
     
     # Tax credits
     - id: basic_allowance
       label: Basic Tax Allowance
       type: credit
       direction: employee
       amount: min(gross, TAX_FREE_THRESHOLD) * INCOME_TAX_RATE
     
     # Employer-side contributions
     - id: employer_contribution
       label: Employer Contribution
       type: percentage
       direction: employer
       rate: EMPLOYER_CONTRIBUTION_RATE
       base: gross
   ```

6. **Test your rule set** using the calculator API or CLI.

7. **Validate your rule set** against the schema:
   ```
   python -m src.payroll_tax_calculator.validate dsl/XX2024/dsl.yaml
   ```

## Troubleshooting

### Common Issues

1. **Rule not applying as expected**:
   - Check the condition to ensure it's correctly formulated
   - Verify that the flags are being passed correctly
   - Check for typos in variable or flag names

2. **Calculation results are incorrect**:
   - Verify the formulas in your rules
   - Check that variables have the correct values
   - Ensure that the rule direction (employee/employer) is set correctly

3. **Syntax errors**:
   - Ensure your YAML is properly formatted
   - Check for missing required fields
   - Verify that expressions are valid

### Validation Errors

The DSL validator may report errors like:

- **Missing required field**: Ensure all required fields are present for each rule type
- **Invalid rule type**: Rule type must be one of the supported types (percentage, credit)
- **Invalid direction**: Direction must be one of: employee, employer, neutral
- **Invalid expression**: Check the syntax of your formulas and conditions

### Debugging Tips

1. Start with a simple rule set and add complexity gradually
2. Use comments to document the purpose of each rule and variable
3. Test your rules with different input scenarios
4. Compare your results with manual calculations to verify correctness
