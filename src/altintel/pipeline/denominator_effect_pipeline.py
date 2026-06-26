from __future__ import annotations

from altintel.analytics.denominator import analyze_denominator_effect
from altintel.analytics.prospects import rank_opportunities_for_portfolio
from altintel.core import AppConfig, DenominatorEffectResult
from altintel.data.sample_data import load_opportunity_registry, load_portfolio_snapshot


def run_denominator_effect_pipeline(
    config: AppConfig,
    portfolio_case: str = "balanced_institution",
    public_market_drawdown_pct: float = 0.25,
    reserve_haircut_pct: float = 0.1,
) -> DenominatorEffectResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    opportunities = load_opportunity_registry()
    ranking = rank_opportunities_for_portfolio(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunities=opportunities,
    )
    base_scores = {entry.opportunity_id: entry.composite_score for entry in ranking.opportunities}
    policy = config.portfolio_policy["policy"]
    return analyze_denominator_effect(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunities=opportunities,
        base_scores=base_scores,
        target_private_markets_pct=float(policy["target_private_markets_pct"]),
        public_market_drawdown_pct=public_market_drawdown_pct,
        reserve_haircut_pct=reserve_haircut_pct,
    )
