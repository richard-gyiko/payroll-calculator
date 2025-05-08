from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Protocol

from .safe_eval import compile_safe_expr


@dataclass(frozen=True)
class CompiledRule:
    """A fully-prepared, immutable rule ready for execution."""

    id: str
    label: str
    direction: str  # "employee" | "employer" | "neutral"
    amount_fn: Callable[[Dict[str, Any], Dict[str, float]], float]
    condition_fn: Callable[[Dict[str, Any], Dict[str, float]], bool]

    def amount(self, ctx: Dict[str, Any], results: Dict[str, float]) -> float:
        return self.amount_fn(ctx, results) if self.condition_fn(ctx, results) else 0.0


# ---------------------------------------------------------------------------
# Plug-in infrastructure
# ---------------------------------------------------------------------------

_RULE_REGISTRY: Dict[str, "RuleType"] = {}


class RuleType(Protocol):
    """Typing-only interface; real classes also expose ``register``."""

    key: str

    @classmethod
    def compile(
        cls, spec: Dict[str, Any], variables: Dict[str, Any]
    ) -> CompiledRule: ...  # noqa: E501

    @classmethod
    def register(cls) -> None: ...


# ---------------------------------------------------------------------------
# Helper mix-in to avoid repeating ``register`` boilerplate
# ---------------------------------------------------------------------------


class _Registrable:
    """Mixin that provides a default ``register`` implementation."""

    key: str  # subclasses must define

    @classmethod
    def register(cls):  # type: ignore[override]
        if not hasattr(cls, "key"):
            raise AttributeError(f"{cls.__name__} is missing class attribute 'key'")
        _RULE_REGISTRY[cls.key] = cls  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Built-in rule types – Percentage and Credit
# ---------------------------------------------------------------------------


class PercentageRule(_Registrable):
    """± *rate* % of *base*. Direction decides the sign."""

    key = "percentage"

    @classmethod
    def compile(cls, spec: Dict[str, Any], variables: Dict[str, Any]) -> CompiledRule:  # noqa: D401,E501
        rid = spec["id"]
        label = spec.get("label", rid)
        rate_fn = compile_safe_expr(spec["rate"], variables)
        base_fn = compile_safe_expr(spec.get("base", "gross"), variables)
        cond_fn = (lambda *_: True) if "condition" not in spec else compile_safe_expr(spec["condition"], variables)
        direction: str = spec.get("direction", "employee")
        if direction not in {"employee", "employer", "neutral"}:
            raise ValueError(f"{rid}: invalid direction {direction}")
        sign = -1 if direction == "employee" else +1

        def amount_fn(ctx, results, rf=rate_fn, bf=base_fn, s=sign):
            return s * rf(ctx, results) * bf(ctx, results)

        return CompiledRule(rid, label, direction, amount_fn, cond_fn)


class CreditRule(_Registrable):
    """A positive or negative amount added to the result set."""

    key = "credit"

    @classmethod
    def compile(cls, spec: Dict[str, Any], variables: Dict[str, Any]) -> CompiledRule:  # noqa: D401,E501
        rid = spec["id"]
        label = spec.get("label", rid)
        amt_fn = compile_safe_expr(spec["amount"], variables)
        cond_fn = (lambda *_: True) if "condition" not in spec else compile_safe_expr(spec["condition"], variables)

        direction = spec.get("direction", "neutral")  # accept employer/employee
        if direction not in {"employee", "employer", "neutral"}:
            raise ValueError(f"{rid}: invalid direction {direction}")
        return CompiledRule(rid, label, direction, amt_fn, cond_fn)


# Register built-in types ----------------------------------------------------
PercentageRule.register()
CreditRule.register()

# Public exports -------------------------------------------------------------
__all__: List[str] = [
    "CompiledRule",
    "RuleType",
    "_RULE_REGISTRY",
    "PercentageRule",
    "CreditRule",
]
