# loader.py
"""Load payroll rules from a JSON file into executable :class:`CompiledRule`s."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .rules import _RULE_REGISTRY, CompiledRule

# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------


_COMMENT_RE = re.compile(
    r"""
    (//[^\n]*$)           |   # // line comments
    (/\*.*?\*/)               # /* block comments */
    """,
    re.MULTILINE | re.DOTALL | re.VERBOSE,
)


def _strip_json_comments(text: str) -> str:
    """Return *text* with //... and /*...*/ comments removed."""
    return re.sub(_COMMENT_RE, "", text)


def load_rules(
    config_path: str | Path,
) -> Tuple[List[CompiledRule], Dict[str, Any], Dict[str, Any]]:
    """Return (compiled_rules, meta, variables) from *config_path*."""
    data = json.loads(_strip_json_comments(Path(config_path).read_text("utf-8")))

    variables: Dict[str, Any] = data.get("variables", {})
    rule_specs: List[Dict[str, Any]] = data["rules"]
    compiled: List[CompiledRule] = []

    for spec in rule_specs:
        rtype = spec["type"]
        if rtype not in _RULE_REGISTRY:
            raise KeyError(
                f"Unknown rule type: {rtype}. Did you forget to register a plugin?"
            )
        compiled.append(_RULE_REGISTRY[rtype].compile(spec, variables))

    return compiled, data.get("meta", {}), variables
