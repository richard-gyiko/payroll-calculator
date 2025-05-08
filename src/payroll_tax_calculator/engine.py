from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .loader import load_rules
from .rules import CompiledRule

__all__ = ["PayrollEngine"]


class PayrollEngine:
    """Run :class:`CompiledRule`s on a salary scenario and return the result."""

    def __init__(self, rules: List[CompiledRule]):
        self.rules = rules

    @classmethod
    def from_yaml(cls, config_path: str | Path):
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
        
        # Sort breakdown values: employee items first, then employer items
        # Within each group, sort by absolute amount value in descending order
        sorted_breakdown = {}
        
        # First, get all items and sort them
        breakdown_items = list(breakdown.items())
        
        # Sort by direction (employee first) and then by absolute amount in descending order
        sorted_items = sorted(
            breakdown_items,
            key=lambda x: (
                0 if x[1]["direction"] == "employee" else 1,  # Employee first (0), then employer (1)
                -abs(x[1]["amount"])  # Sort by absolute amount in descending order
            )
        )
        
        # Rebuild the dictionary with the sorted items
        for key, value in sorted_items:
            sorted_breakdown[key] = value
            
        return {
            "gross": gross,
            "net": net,
            "super_gross": cost,
            "breakdown": sorted_breakdown,
        }

    def get_flags(self) -> List[str]:
        """Extract and return all flag names used in rule conditions."""
        flags = set()

        for rule in self.rules:
            # Extract flags from condition function's docstring
            if hasattr(rule.condition_fn, "__doc__") and rule.condition_fn.__doc__:
                flags.update(
                    self._extract_flags_from_docstring(rule.condition_fn.__doc__)
                )

            # Extract flags from amount function's docstring
            if hasattr(rule.amount_fn, "__doc__") and rule.amount_fn.__doc__:
                flags.update(self._extract_flags_from_docstring(rule.amount_fn.__doc__))

        return sorted(list(flags))

    @staticmethod
    def _extract_flags_from_docstring(docstring: str) -> set[str]:
        """Helper method to extract flag names from a docstring."""
        flags = set()
        if "flags." in docstring:
            for part in docstring.split("flags.")[1:]:
                flag_name = ""
                for char in part:
                    if char.isalnum() or char == "_":
                        flag_name += char
                    else:
                        break
                if flag_name:
                    flags.add(flag_name)
        return flags
