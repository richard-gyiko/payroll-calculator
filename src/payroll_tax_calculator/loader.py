from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from ruamel.yaml import YAML

from .rules import _RULE_REGISTRY, CompiledRule

# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------


def load_rules(
    config_path: str | Path,
) -> Tuple[List[CompiledRule], Dict[str, Any], Dict[str, Any]]:
    """Return (compiled_rules, meta, variables) from *config_path*.

    Supports YAML (.yaml, .yml) file formats.
    """
    path = Path(config_path)

    # Ensure file has YAML extension
    if path.suffix.lower() not in (".yaml", ".yml"):
        raise ValueError(
            f"Unsupported file format: {path.suffix}. Only YAML (.yaml, .yml) files are supported."
        )

    # Load YAML file
    yaml = YAML(typ="safe")
    data = yaml.load(path.read_text("utf-8"))

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
