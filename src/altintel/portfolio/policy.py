from __future__ import annotations

from altintel.core.models import (
    CashflowForecast,
    InvestmentMemoInput,
    PolicyCheck,
    PolicyEvaluation,
    PortfolioSnapshot,
)


def evaluate_portfolio_policy(
    portfolio: PortfolioSnapshot,
    proposed_commitment: InvestmentMemoInput,
    forecast: CashflowForecast,
    policy: dict[str, float],
) -> PolicyEvaluation:
    total_nav = portfolio.total_nav_mn
    commitment_pct_nav = proposed_commitment.commitment_size_mn / total_nav if total_nav else 0.0
    max_single_fund_pct_nav = float(policy["max_single_fund_pct_nav"])
    single_fund_status = "pass" if commitment_pct_nav <= max_single_fund_pct_nav else "breach"

    horizon_months = int(policy["min_liquidity_coverage_months"])
    horizon_points = forecast.forecast_points[:horizon_months]
    net_calls = sum(point.contribution_mn - point.distribution_mn for point in horizon_points)
    liquidity_coverage_months = (
        portfolio.liquid_reserves_mn / (net_calls / horizon_months) if horizon_months and net_calls > 0 else 999.0
    )
    liquidity_status = "pass" if liquidity_coverage_months >= horizon_months else "breach"

    private_markets_pct = total_nav / (total_nav + portfolio.liquid_reserves_mn) if (total_nav + portfolio.liquid_reserves_mn) else 0.0
    target_private_markets_pct = float(policy["target_private_markets_pct"])
    target_status = "pass" if private_markets_pct >= target_private_markets_pct else "watch"

    checks = [
        PolicyCheck(
            name="max_single_fund_pct_nav",
            status=single_fund_status,
            metric_value=round(commitment_pct_nav, 4),
            threshold_value=max_single_fund_pct_nav,
            message="Proposed commitment size as a share of portfolio NAV.",
        ),
        PolicyCheck(
            name="min_liquidity_coverage_months",
            status=liquidity_status,
            metric_value=round(liquidity_coverage_months, 4),
            threshold_value=float(horizon_months),
            message="Liquid reserves divided by average monthly net cash outflow over the downside horizon.",
        ),
        PolicyCheck(
            name="target_private_markets_pct",
            status=target_status,
            metric_value=round(private_markets_pct, 4),
            threshold_value=target_private_markets_pct,
            message="Current private-markets NAV share versus long-term target.",
        ),
    ]
    return PolicyEvaluation(checks=checks)
