from altintel.analytics.liquidity import run_liquidity_stress
from altintel.cashflows.forecasting import forecast_commitment_cashflows
from altintel.data.sample_data import (
    load_cashflow_assumptions,
    load_portfolio_snapshot,
    load_proposed_commitment,
)
from altintel.portfolio.analysis import add_proposed_commitment, summarize_portfolio


def test_cashflow_forecast_reaches_target_commitment() -> None:
    memo = load_proposed_commitment()
    assumptions = load_cashflow_assumptions()
    portfolio = load_portfolio_snapshot()

    forecast = forecast_commitment_cashflows(memo, assumptions["base_case"], portfolio.as_of)

    total_contributions = sum(point.contribution_mn for point in forecast.forecast_points)
    assert round(total_contributions, 4) == memo.commitment_size_mn
    assert forecast.peak_nav_mn > 0
    assert forecast.dpi > 1.0


def test_portfolio_summary_and_liquidity_stress() -> None:
    memo = load_proposed_commitment()
    assumptions = load_cashflow_assumptions()
    portfolio = load_portfolio_snapshot()
    updated_portfolio = add_proposed_commitment(portfolio, memo)

    summary = summarize_portfolio(updated_portfolio)
    downside_forecast = forecast_commitment_cashflows(memo, assumptions["downside_case"], portfolio.as_of)
    stress = run_liquidity_stress(updated_portfolio, downside_forecast, assumptions["liquidity_stress"])

    assert summary.total_unfunded_mn == 336.0
    assert summary.infrastructure_nav_mn == 234.0
    assert stress.projected_calls_mn > 0
    assert stress.ending_liquidity_mn > 0
