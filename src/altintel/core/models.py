from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class InvestmentMemoInput:
    document_id: str
    fund_name: str
    strategy: str
    geography: str
    currency: str
    commitment_size_mn: float
    vintage_year: int
    source_text: str


@dataclass(slots=True)
class EvidenceItem:
    quote: str
    section: str


@dataclass(slots=True)
class ExtractedFundFacts:
    fund_name: str
    strategy: str
    geography: str
    target_size_mn: float
    gp_commitment_pct: float
    management_fee_pct: float
    carry_pct: float
    term_years: int
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass(slots=True)
class RiskFinding:
    category: str
    severity: str
    title: str
    rationale: str
    mitigants: list[str] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass(slots=True)
class DueDiligenceReport:
    facts: ExtractedFundFacts
    risks: list[RiskFinding]
    overall_risk_rating: str
    validation_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CashflowPoint:
    as_of: date
    contribution_mn: float
    distribution_mn: float
    nav_mn: float


@dataclass(slots=True)
class CashflowForecast:
    fund_name: str
    forecast_points: list[CashflowPoint]
    peak_nav_mn: float
    dpi: float
    tvpi: float


@dataclass(slots=True)
class PortfolioHolding:
    name: str
    strategy: str
    nav_mn: float
    unfunded_mn: float


@dataclass(slots=True)
class PortfolioSnapshot:
    as_of: date
    total_nav_mn: float
    liquid_reserves_mn: float
    holdings: list[PortfolioHolding] = field(default_factory=list)


@dataclass(slots=True)
class PortfolioSummary:
    total_nav_mn: float
    total_unfunded_mn: float
    liquid_reserves_mn: float
    infrastructure_nav_mn: float
    infrastructure_pct_nav: float


@dataclass(slots=True)
class LiquidityStressResult:
    scenario_name: str
    starting_liquidity_mn: float
    projected_calls_mn: float
    projected_distributions_mn: float
    ending_liquidity_mn: float
    liquidity_coverage_ratio: float
    breach: bool
