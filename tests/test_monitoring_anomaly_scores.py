from altintel.analytics.monitoring import build_data_driven_insights
from altintel.data.sample_data import load_portfolio_snapshot
from altintel.data.simulation import generate_portfolio_monitoring_data


def test_anomaly_scores_are_ranked_and_populated() -> None:
    portfolio = load_portfolio_snapshot(case_name="balanced_institution")
    observations = generate_portfolio_monitoring_data(portfolio, quarters=8, seed=7)
    insights = build_data_driven_insights(observations, portfolio.liquid_reserves_mn)

    assert insights.anomaly_scores
    assert insights.anomaly_scores[0].anomaly_score >= insights.anomaly_scores[-1].anomaly_score
    assert insights.anomaly_scores[0].label in {"low", "medium", "high"}
