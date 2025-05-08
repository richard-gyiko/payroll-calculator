# engine.py
"""Execution engine + CLI wrapper for the JSON‑defined payroll rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from loader import load_rules
from rules import CompiledRule

__all__ = ["PayrollEngine"]


class PayrollEngine:
    """Run :class:`CompiledRule`s on a salary scenario and return the result."""

    def __init__(self, rules: List[CompiledRule]):
        self.rules = rules

    @classmethod
    def from_json(cls, config_path: str | Path):
        compiled, *_ = load_rules(config_path)
        return cls(compiled)

    def run(self, gross: int | float, **flags) -> Dict[str, Any]:
        ctx: Dict[str, Any] = {"gross": gross, "flags": flags}
        breakdown: Dict[str, float] = {}
        employer_total = 0.0
        employee_total = 0.0

        for rule in self.rules:
            amt = rule.amount(ctx, breakdown)
            if not amt:
                continue
            breakdown[rule.id] = {
                "label": rule.label,
                "amount": amt,
                "direction": rule.direction,
            }
            if rule.direction == "employer":
                employer_total += amt
            else:  # employee side (deduction or credit)
                employee_total += amt

        net = gross + employee_total
        cost = gross + employer_total
        return {
            "gross": gross,
            "net": net,
            "super_gross": cost,
            "breakdown": breakdown,
        }

    def get_flags(self) -> List[str]:
        """Extract and return all flag names used in rule conditions."""
        flags = set()

        # Examine each rule's condition function's docstring
        # The docstring contains the original expression
        for rule in self.rules:
            if hasattr(rule.condition_fn, "__doc__") and rule.condition_fn.__doc__:
                condition_expr = rule.condition_fn.__doc__
                if "flags." in condition_expr:
                    # Extract flag names from expressions like flags.under25, flags.children, etc.
                    for part in condition_expr.split("flags.")[1:]:
                        # Extract the flag name (stops at space, operator, etc.)
                        flag_name = ""
                        for char in part:
                            if char.isalnum() or char == "_":
                                flag_name += char
                            else:
                                break
                        if flag_name:
                            flags.add(flag_name)

        return sorted(list(flags))
