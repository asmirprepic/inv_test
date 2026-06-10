from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from datetime import date

from altintel.core.models import InvestmentMemoInput, PortfolioHolding, PortfolioSnapshot


DATA_ROOT = Path("data")
SAMPLE_DOCUMENTS_DIR = DATA_ROOT / "sample_documents"
SYNTHETIC_DIR = DATA_ROOT / "synthetic"
DEFAULT_PORTFOLIO_CASE = "balanced_institution"
DEFAULT_COMMITMENT_CASE = "infrastructure"


def load_text_document(path: str | Path) -> str:
    document_path = Path(path)
    return document_path.read_text(encoding="utf-8")


def load_json(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    with json_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_proposed_commitment(path: str | Path = SYNTHETIC_DIR / "proposed_commitment.json") -> InvestmentMemoInput:
    payload = load_json(path)
    source_text = load_text_document(payload["source_document_path"])
    return InvestmentMemoInput(
        document_id=payload["document_id"],
        fund_name=payload["fund_name"],
        strategy=payload["strategy"],
        geography=payload["geography"],
        currency=payload["currency"],
        commitment_size_mn=payload["commitment_size_mn"],
        vintage_year=payload["vintage_year"],
        source_text=source_text,
    )


def _commitment_case_path(case_name: str) -> Path:
    return SYNTHETIC_DIR / f"proposed_commitment_{case_name}.json"


def list_commitment_cases() -> list[str]:
    cases: list[str] = []
    for path in sorted(SYNTHETIC_DIR.glob("proposed_commitment_*.json")):
        cases.append(path.stem.removeprefix("proposed_commitment_"))
    return cases


def load_named_proposed_commitment(
    path: str | Path | None = None,
    case_name: str = DEFAULT_COMMITMENT_CASE,
) -> InvestmentMemoInput:
    commitment_path = Path(path) if path is not None else _commitment_case_path(case_name)
    if not commitment_path.exists() and path is None and case_name == DEFAULT_COMMITMENT_CASE:
        commitment_path = SYNTHETIC_DIR / "proposed_commitment.json"
    return load_proposed_commitment(commitment_path)


def _portfolio_case_path(case_name: str) -> Path:
    return SYNTHETIC_DIR / f"portfolio_{case_name}.json"


def list_portfolio_cases() -> list[str]:
    cases: list[str] = []
    for path in sorted(SYNTHETIC_DIR.glob("portfolio_*.json")):
        case_name = path.stem.removeprefix("portfolio_")
        if case_name == "snapshot":
            continue
        cases.append(case_name)
    return cases


def load_portfolio_snapshot(
    path: str | Path | None = None,
    case_name: str = DEFAULT_PORTFOLIO_CASE,
) -> PortfolioSnapshot:
    portfolio_path = Path(path) if path is not None else _portfolio_case_path(case_name)
    if not portfolio_path.exists() and path is None and case_name == DEFAULT_PORTFOLIO_CASE:
        portfolio_path = SYNTHETIC_DIR / "portfolio_snapshot.json"
    payload = load_json(portfolio_path)
    holdings = [
        PortfolioHolding(
            name=row["name"],
            strategy=row["strategy"],
            nav_mn=row["nav_mn"],
            unfunded_mn=row["unfunded_mn"],
        )
        for row in payload["holdings"]
    ]
    return PortfolioSnapshot(
        as_of=date.fromisoformat(payload["as_of"]),
        total_nav_mn=payload["total_nav_mn"],
        liquid_reserves_mn=payload["liquid_reserves_mn"],
        holdings=holdings,
    )


def load_cashflow_assumptions(path: str | Path = SYNTHETIC_DIR / "cashflow_assumptions.json") -> dict[str, Any]:
    return load_json(path)
