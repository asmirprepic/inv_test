from __future__ import annotations

from altintel.core.models import CashflowForecast, LiquidityStressResult, PortfolioSnapshot


def run_liquidity_stress(
    portfolio: PortfolioSnapshot,
    forecast: CashflowForecast,
    stress_assumptions: dict[str, float],
) -> LiquidityStressResult:
    horizon_months = int(stress_assumptions["stress_horizon_months"])
    near_term_points = forecast.forecast_points[:horizon_months]

    projected_calls = sum(point.contribution_mn for point in near_term_points)
    projected_distributions = sum(point.distribution_mn for point in near_term_points)

    stressed_calls = projected_calls * float(stress_assumptions["near_term_call_multiplier"])
    stressed_distributions = projected_distributions * float(
        stress_assumptions["near_term_distribution_multiplier"]
    )
    ending_liquidity = portfolio.liquid_reserves_mn - stressed_calls + stressed_distributions
    coverage_ratio = ending_liquidity / stressed_calls if stressed_calls else 0.0

    return LiquidityStressResult(
        scenario_name="liquidity_stress",
        starting_liquidity_mn=portfolio.liquid_reserves_mn,
        projected_calls_mn=round(stressed_calls, 4),
        projected_distributions_mn=round(stressed_distributions, 4),
        ending_liquidity_mn=round(ending_liquidity, 4),
        liquidity_coverage_ratio=round(coverage_ratio, 4),
        breach=ending_liquidity < 0,
    )
