from altintel.analytics.monitoring import build_data_driven_insights
from altintel.data.sample_data import load_portfolio_snapshot
from altintel.data.simulation import generate_portfolio_monitoring_data


def test_generate_monitoring_data_and_insights() -> None:
    portfolio = load_portfolio_snapshot(case_name="balanced_institution")
    observations = generate_portfolio_monitoring_data(portfolio, quarters=8, seed=3)
    insights = build_data_driven_insights(observations, portfolio.liquid_reserves_mn)

    assert len(observations) == len(portfolio.holdings) * 8
    assert len(insights.strategy_signals) >= 4
    assert insights.portfolio_cash_burn_ratio > 0
