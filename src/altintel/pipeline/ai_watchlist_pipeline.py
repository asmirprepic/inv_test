from __future__ import annotations

from altintel.analytics.monitoring import build_data_driven_insights
from altintel.analytics.watchlist import build_ai_watchlist
from altintel.core import AIWatchlistResult
from altintel.data.sample_data import load_portfolio_snapshot
from altintel.data.simulation import generate_portfolio_monitoring_data


def run_ai_watchlist_pipeline(
    portfolio_case: str = "balanced_institution",
    quarters: int = 12,
    seed: int = 7,
) -> AIWatchlistResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    observations = generate_portfolio_monitoring_data(portfolio, quarters=quarters, seed=seed)
    insights = build_data_driven_insights(observations, portfolio.liquid_reserves_mn)
    return build_ai_watchlist(portfolio_case=portfolio_case, insights=insights)
