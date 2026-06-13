from __future__ import annotations

from dataclasses import dataclass

from altintel.analytics.monitoring import build_data_driven_insights
from altintel.analytics.liquidity import run_liquidity_stress
from altintel.cashflows.forecasting import forecast_commitment_cashflows
from altintel.core import (
    AppConfig,
    AnnualPacingAnalysis,
    DataDrivenInsights,
    DueDiligenceReport,
    LiquidityStressResult,
    PolicyEvaluation,
    PortfolioSummary,
)
from altintel.data.simulation import generate_portfolio_monitoring_data
from altintel.data.sample_data import (
    load_cashflow_assumptions,
    load_named_proposed_commitment,
    load_portfolio_snapshot,
)
from altintel.due_diligence.service import run_due_diligence
from altintel.portfolio.analysis import add_proposed_commitment, summarize_portfolio
from altintel.portfolio.pacing import analyze_annual_pacing
from altintel.portfolio.policy import evaluate_portfolio_policy


@dataclass(slots=True)
class FullPipelineResult:
    due_diligence: DueDiligenceReport
    portfolio_before: PortfolioSummary
    portfolio_after: PortfolioSummary
    base_case_peak_nav_mn: float
    base_case_dpi: float
    base_case_tvpi: float
    downside_case_peak_nav_mn: float
    downside_case_tvpi: float
    liquidity_stress: LiquidityStressResult
    policy_evaluation: PolicyEvaluation
    data_driven_insights: DataDrivenInsights
    annual_pacing: AnnualPacingAnalysis


def run_full_pipeline(
    config: AppConfig,
    portfolio_case: str = "balanced_institution",
    commitment_case: str = "infrastructure",
) -> FullPipelineResult:
    memo = load_named_proposed_commitment(case_name=commitment_case)
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    assumptions = load_cashflow_assumptions()

    due_diligence = run_due_diligence(memo, config)
    portfolio_before = summarize_portfolio(portfolio)
    portfolio_with_commitment = add_proposed_commitment(portfolio, memo)
    portfolio_after = summarize_portfolio(portfolio_with_commitment)

    base_case = forecast_commitment_cashflows(memo, assumptions["base_case"], portfolio.as_of)
    downside_case = forecast_commitment_cashflows(memo, assumptions["downside_case"], portfolio.as_of)
    liquidity_stress = run_liquidity_stress(
        portfolio_with_commitment,
        downside_case,
        assumptions["liquidity_stress"],
    )
    policy_evaluation = evaluate_portfolio_policy(
        portfolio=portfolio_with_commitment,
        proposed_commitment=memo,
        forecast=downside_case,
        policy=config.portfolio_policy["policy"],
    )
    pacing_config = config.base["pipeline"]["pacing"]
    annual_pacing = analyze_annual_pacing(
        memo=memo,
        forecast=base_case,
        current_unfunded_mn=portfolio_before.total_unfunded_mn,
        annual_commitment_budget_mn=float(pacing_config["annual_commitment_budget_mn"]),
        reserve_buffer_pct=float(pacing_config["reserve_buffer_pct"]),
        pacing_years=int(pacing_config["pacing_years"]),
    )
    monitoring_observations = generate_portfolio_monitoring_data(portfolio_with_commitment)
    data_driven_insights = build_data_driven_insights(
        observations=monitoring_observations,
        liquid_reserves_mn=portfolio_with_commitment.liquid_reserves_mn,
    )

    return FullPipelineResult(
        due_diligence=due_diligence,
        portfolio_before=portfolio_before,
        portfolio_after=portfolio_after,
        base_case_peak_nav_mn=base_case.peak_nav_mn,
        base_case_dpi=base_case.dpi,
        base_case_tvpi=base_case.tvpi,
        downside_case_peak_nav_mn=downside_case.peak_nav_mn,
        downside_case_tvpi=downside_case.tvpi,
        liquidity_stress=liquidity_stress,
        policy_evaluation=policy_evaluation,
        data_driven_insights=data_driven_insights,
        annual_pacing=annual_pacing,
    )
