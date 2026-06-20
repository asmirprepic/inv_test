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


@dataclass(slots=True)
class PolicyCheck:
    name: str
    status: str
    metric_value: float
    threshold_value: float
    message: str


@dataclass(slots=True)
class PolicyEvaluation:
    checks: list[PolicyCheck]


@dataclass(slots=True)
class HoldingObservation:
    as_of: date
    holding_name: str
    strategy: str
    nav_mn: float
    contribution_mn: float
    distribution_mn: float
    revenue_growth_pct: float
    ebitda_margin_pct: float
    leverage_ratio: float
    valuation_change_pct: float


@dataclass(slots=True)
class MonitoringAlert:
    holding_name: str
    as_of: date
    severity: str
    metric: str
    message: str


@dataclass(slots=True)
class StrategySignal:
    strategy: str
    observation_count: int
    avg_revenue_growth_pct: float
    avg_distribution_yield_pct: float
    avg_leverage_ratio: float
    nav_volatility_pct: float


@dataclass(slots=True)
class DataDrivenInsights:
    observations: list[HoldingObservation]
    strategy_signals: list[StrategySignal]
    alerts: list[MonitoringAlert]
    anomaly_scores: list["HoldingAnomalyScore"]
    portfolio_cash_burn_ratio: float


@dataclass(slots=True)
class PortfolioCaseComparison:
    portfolio_case: str
    commitment_case: str
    suitability_score: float
    policy_breach_count: int
    policy_watch_count: int
    monitoring_alert_count: int
    high_severity_alert_count: int
    ending_liquidity_mn: float
    liquidity_breach: bool
    cash_burn_ratio: float
    concentration_pct_nav: float


@dataclass(slots=True)
class PortfolioComparisonResult:
    comparisons: list[PortfolioCaseComparison]


@dataclass(slots=True)
class HoldingAnomalyScore:
    holding_name: str
    strategy: str
    as_of: date
    anomaly_score: float
    revenue_growth_deviation: float
    leverage_deviation: float
    valuation_deviation: float
    distribution_deviation: float
    label: str


@dataclass(slots=True)
class PortfolioCaseTimeSeriesPoint:
    portfolio_case: str
    as_of: date
    holdings_count: int
    total_nav_mn: float
    total_contributions_mn: float
    total_distributions_mn: float
    net_cash_burn_mn: float
    cash_burn_ratio: float
    alert_count: int
    high_severity_alert_count: int


@dataclass(slots=True)
class PortfolioCaseTimeSeries:
    portfolio_case: str
    commitment_case: str
    points: list[PortfolioCaseTimeSeriesPoint]


@dataclass(slots=True)
class PortfolioCasesTimeSeriesComparison:
    series: list[PortfolioCaseTimeSeries]


@dataclass(slots=True)
class AnnualPacingPoint:
    year: int
    commitment_budget_mn: float
    proposed_commitment_mn: float
    called_capital_mn: float
    distributions_mn: float
    net_cash_outflow_mn: float
    ending_unfunded_mn: float
    reserve_buffer_mn: float


@dataclass(slots=True)
class AnnualPacingAnalysis:
    annual_commitment_budget_mn: float
    reserve_buffer_pct: float
    points: list[AnnualPacingPoint]


@dataclass(slots=True)
class WatchlistReason:
    category: str
    signal_strength: float
    message: str


@dataclass(slots=True)
class WatchlistEntry:
    holding_name: str
    strategy: str
    as_of: date
    priority_score: float
    priority_label: str
    recommended_action: str
    reasons: list[WatchlistReason]


@dataclass(slots=True)
class AIWatchlistResult:
    portfolio_case: str
    generated_as_of: date
    portfolio_cash_burn_ratio: float
    entries: list[WatchlistEntry]


@dataclass(slots=True)
class Prospect:
    prospect_id: str
    fund_name: str
    strategy: str
    geography: str
    status: str
    target_size_mn: float
    proposed_commitment_mn: float
    gp_commitment_pct: float
    management_fee_pct: float
    carry_pct: float
    team_score: float
    track_record_score: float
    esg_score: float
    portfolio_fit_score: float
    liquidity_impact_score: float
    overlap_risk_score: float
    dd_score: float
    tags: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass(slots=True)
class ProspectRankingReason:
    category: str
    score_impact: float
    message: str


@dataclass(slots=True)
class RankedProspect:
    prospect_id: str
    fund_name: str
    strategy: str
    geography: str
    status: str
    composite_score: float
    recommended_action: str
    reasons: list[ProspectRankingReason]


@dataclass(slots=True)
class ProspectRankingResult:
    portfolio_case: str
    prospects: list[RankedProspect]


@dataclass(slots=True)
class ProspectSearchMatch:
    prospect_id: str
    fund_name: str
    strategy: str
    geography: str
    status: str
    match_score: float
    matched_terms: list[str]
    summary: str


@dataclass(slots=True)
class ProspectSearchResult:
    query: str
    matches: list[ProspectSearchMatch]
