from __future__ import annotations

import ast
import math
from types import SimpleNamespace
from typing import Any, Callable, Mapping, Tuple

__all__ = ["SafeEvalError", "safe_eval", "compile_safe_expr"]


# ──────────────────── error type ──────────────────────────────────────────
class SafeEvalError(RuntimeError):
    """Expression contained a disallowed construct."""


# ──────────────────── whitelist tables ────────────────────────────────────
_ALLOWED_NODES: set[type[ast.AST]] = {
    ast.Expression,
    ast.Constant,
    ast.Name,
    ast.BinOp,
    ast.UnaryOp,
    ast.BoolOp,
    ast.Compare,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.UAdd,
    ast.USub,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Gt,
    ast.GtE,
    ast.Lt,
    ast.LtE,
    ast.Call,
    ast.Load,
    ast.Subscript,
    ast.Attribute,
}

_ALLOWED_UNARY_OPS: Tuple[type[ast.unaryop], ...] = (ast.UAdd, ast.USub, ast.Not)

_ALLOWED_FUNCTIONS: dict[str, Any] = {
    "abs": abs,
    "ceil": math.ceil,
    "floor": math.floor,
    "round": round,
    "sqrt": math.sqrt,
    "min": min,
    "max": max,
}

# allow lowercase literals in the DSL
_ALLOWED_CONSTANTS: Mapping[str, Any] = {
    "true": True,
    "false": False,
    "null": None,
}


# ──────────────────── AST validator ───────────────────────────────────────
class _Validator(ast.NodeVisitor):
    def generic_visit(self, node: ast.AST) -> None:  # noqa: D401
        if type(node) not in _ALLOWED_NODES:
            raise SafeEvalError(f"Disallowed expression node: {type(node).__name__}")
        super().generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if type(node.op) not in _ALLOWED_UNARY_OPS:
            raise SafeEvalError(f"Disallowed unary operator: {type(node.op).__name__}")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # deny hidden / dunder attributes like __class__
        if node.attr.startswith("_"):
            raise SafeEvalError("Access to private attributes is forbidden")
        self.generic_visit(node)


# ──────────────────── internal helpers ────────────────────────────────────
def _to_namespace(value: Any) -> Any:
    """Recursively convert dicts to SimpleNamespace for attr-style access."""
    if isinstance(value, Mapping):
        return SimpleNamespace(**{k: _to_namespace(v) for k, v in value.items()})
    return value


def _compile(expr: str) -> ast.CodeType:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise SafeEvalError(f"Invalid expression: {exc}") from None
    _Validator().visit(tree)
    return compile(tree, "<expr>", "eval")


# ──────────────────── public helpers ──────────────────────────────────────
def safe_eval(expr: Any, local_env: Mapping[str, Any] | None = None) -> Any:
    """Evaluate *expr* immediately in a restricted environment."""
    # literal numbers / bools bypass AST
    if not isinstance(expr, str):
        return expr

    code = _compile(expr)
    env = {**_ALLOWED_CONSTANTS, **(local_env or {})}

    # convert nested dicts so flags.child works
    for k, v in list(env.items()):
        env[k] = _to_namespace(v)

    return eval(code, {"__builtins__": {}}, {**_ALLOWED_FUNCTIONS, **env})


def compile_safe_expr(
    expr: Any,
    constants: Mapping[str, Any] | None = None,
) -> Callable[[dict, dict], Any]:
    """
    Pre-compile *expr* and return ``fn(ctx, results)`` suitable for the engine.

    If *expr* is not a string (i.e. a literal number), the returned function
    just returns that literal.
    """
    # literals: no parsing needed
    if not isinstance(expr, str):
        return lambda _ctx, _results, lit=expr: lit

    code = _compile(expr)
    constants = dict(constants or {})

    def _fn(ctx: dict, results: dict) -> Any:
        env = {
            **_ALLOWED_CONSTANTS,
            **constants,
            **results,  # allow referencing earlier rule amounts
            "gross": ctx["gross"],
            "flags": _to_namespace(ctx["flags"]),
        }
        return eval(code, {"__builtins__": {}}, {**_ALLOWED_FUNCTIONS, **env})

    # Store the original expression in the function's docstring
    # This will be used by get_flags() to extract flag names
    _fn.__doc__ = expr
    return _fn
