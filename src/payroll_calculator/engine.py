# engine.py
"""Execution engine + CLI wrapper for the JSON‑defined payroll rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from loader import load_rules

__all__ = ["PayrollEngine"]


class PayrollEngine:
    """Run :class:`CompiledRule`s on a salary scenario and return the result."""

    def __init__(self, rules):
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
