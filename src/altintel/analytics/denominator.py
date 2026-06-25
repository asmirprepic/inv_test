from __future__ import annotations

from altintel.core.models import (
    DenominatorEffectOpportunityImpact,
    DenominatorEffectResult,
    InvestmentOpportunity,
    PortfolioSnapshot,
)


def _infer_public_nav(private_nav_mn: float, target_private_markets_pct: float) -> float:
    if target_private_markets_pct <= 0 or target_private_markets_pct >= 1:
        raise ValueError("target_private_markets_pct must be between 0 and 1")
    total_fund_nav = private_nav_mn / target_private_markets_pct
    return total_fund_nav - private_nav_mn


def _baseline_private_pct(private_nav_mn: float, public_nav_mn: float) -> float:
    total = private_nav_mn + public_nav_mn
    return private_nav_mn / total if total else 0.0


def _stressed_opportunity_score(
    opportunity: InvestmentOpportunity,
    baseline_score: float,
    stressed_private_pct: float,
    target_private_pct: float,
    stressed_liquid_reserves_mn: float,
) -> tuple[float, str]:
    overweight_gap = max(stressed_private_pct - target_private_pct, 0.0)
    score = baseline_score
    constraint = "none"

    if overweight_gap > 0:
        denominator_penalty = overweight_gap * 140.0
        score -= denominator_penalty
        constraint = "private_markets_overweight"

    if opportunity.liquidity_impact_score >= 6.5:
        score -= opportunity.liquidity_impact_score * 1.3
        constraint = "liquidity_pressure"

    if opportunity.expected_call_profile == "fast":
        score -= 6.5
        constraint = "fast_call_profile"

    if opportunity.proposed_commitment_mn > stressed_liquid_reserves_mn * 0.35:
        score -= 8.0
        constraint = "commitment_size_vs_reserves"

    return round(max(score, 0.0), 4), constraint


def analyze_denominator_effect(
    portfolio_case: str,
    portfolio: PortfolioSnapshot,
    opportunities: list[InvestmentOpportunity],
    base_scores: dict[str, float],
    target_private_markets_pct: float,
    public_market_drawdown_pct: float = 0.25,
    reserve_haircut_pct: float = 0.1,
) -> DenominatorEffectResult:
    baseline_public_nav_mn = _infer_public_nav(portfolio.total_nav_mn, target_private_markets_pct)
    stressed_public_nav_mn = baseline_public_nav_mn * (1 - public_market_drawdown_pct)
    baseline_private_pct = _baseline_private_pct(portfolio.total_nav_mn, baseline_public_nav_mn)
    stressed_private_pct = _baseline_private_pct(portfolio.total_nav_mn, stressed_public_nav_mn)
    overweight_gap_pct = max(stressed_private_pct - target_private_markets_pct, 0.0)
    stressed_liquid_reserves_mn = portfolio.liquid_reserves_mn * (1 - reserve_haircut_pct)

    impacts: list[DenominatorEffectOpportunityImpact] = []
    for opportunity in opportunities:
        base_score = base_scores[opportunity.opportunity_id]
        stressed_score, key_constraint = _stressed_opportunity_score(
            opportunity=opportunity,
            baseline_score=base_score,
            stressed_private_pct=stressed_private_pct,
            target_private_pct=target_private_markets_pct,
            stressed_liquid_reserves_mn=stressed_liquid_reserves_mn,
        )
        if stressed_score >= 58:
            recommendation = "advance"
        elif stressed_score >= 44:
            recommendation = "advance_with_conditions"
        elif stressed_score >= 34:
            recommendation = "hold"
        else:
            recommendation = "defer"
        impacts.append(
            DenominatorEffectOpportunityImpact(
                opportunity_id=opportunity.opportunity_id,
                manager_name=opportunity.manager_name,
                fund_name=opportunity.fund_name,
                base_composite_score=round(base_score, 4),
                stressed_composite_score=stressed_score,
                score_change=round(stressed_score - base_score, 4),
                stressed_recommendation=recommendation,
                key_constraint=key_constraint,
            )
        )

    ordered_impacts = sorted(impacts, key=lambda item: (-item.stressed_composite_score, item.fund_name))
    summary = (
        f"After a {round(public_market_drawdown_pct * 100, 1)}% public-market drawdown, "
        f"private-markets exposure rises from {round(baseline_private_pct * 100, 2)}% to "
        f"{round(stressed_private_pct * 100, 2)}% of total fund NAV."
    )
    return DenominatorEffectResult(
        portfolio_case=portfolio_case,
        public_market_drawdown_pct=public_market_drawdown_pct,
        baseline_private_markets_pct=round(baseline_private_pct, 4),
        stressed_private_markets_pct=round(stressed_private_pct, 4),
        target_private_markets_pct=target_private_markets_pct,
        overweight_gap_pct=round(overweight_gap_pct, 4),
        baseline_public_nav_mn=round(baseline_public_nav_mn, 4),
        stressed_public_nav_mn=round(stressed_public_nav_mn, 4),
        stressed_liquid_reserves_mn=round(stressed_liquid_reserves_mn, 4),
        opportunity_impacts=ordered_impacts,
        summary=summary,
    )
