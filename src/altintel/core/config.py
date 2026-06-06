from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class AppConfig:
    base: dict[str, Any]
    model: dict[str, Any]
    risk_taxonomy: dict[str, Any]
    portfolio_policy: dict[str, Any]


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping at {path}")
    return data


def load_app_config(config_dir: str | Path = "configs") -> AppConfig:
    root = Path(config_dir)
    return AppConfig(
        base=_load_yaml(root / "base.yml"),
        model=_load_yaml(root / "model_config.yml"),
        risk_taxonomy=_load_yaml(root / "risk_taxonomy.yml"),
        portfolio_policy=_load_yaml(root / "portfolio_policy.yml"),
    )
