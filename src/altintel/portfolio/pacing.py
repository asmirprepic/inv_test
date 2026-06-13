from __future__ import annotations

from collections import defaultdict

from altintel.core.models import AnnualPacingAnalysis, AnnualPacingPoint, CashflowForecast, InvestmentMemoInput


def analyze_annual_pacing(
    memo: InvestmentMemoInput,
    forecast: CashflowForecast,
    current_unfunded_mn: float,
    annual_commitment_budget_mn: float,
    reserve_buffer_pct: float,
    pacing_years: int,
) -> AnnualPacingAnalysis:
    by_year: dict[int, dict[str, float]] = defaultdict(lambda: {"calls": 0.0, "dists": 0.0})
    for point in forecast.forecast_points:
        by_year[point.as_of.year]["calls"] += point.contribution_mn
        by_year[point.as_of.year]["dists"] += point.distribution_mn

    years = sorted(by_year)[:pacing_years]
    if not years:
        years = [memo.vintage_year + offset for offset in range(pacing_years)]

    ending_unfunded = current_unfunded_mn + memo.commitment_size_mn
    annual_points: list[AnnualPacingPoint] = []
    first_year = years[0]
    for year in range(first_year, first_year + pacing_years):
        called_capital = round(by_year[year]["calls"], 4)
        distributions = round(by_year[year]["dists"], 4)
        net_cash_outflow = round(called_capital - distributions, 4)
        ending_unfunded = round(max(ending_unfunded - called_capital, 0.0), 4)
        annual_points.append(
            AnnualPacingPoint(
                year=year,
                commitment_budget_mn=annual_commitment_budget_mn,
                proposed_commitment_mn=memo.commitment_size_mn if year == first_year else 0.0,
                called_capital_mn=called_capital,
                distributions_mn=distributions,
                net_cash_outflow_mn=net_cash_outflow,
                ending_unfunded_mn=ending_unfunded,
                reserve_buffer_mn=round(max(net_cash_outflow, 0.0) * reserve_buffer_pct, 4),
            )
        )

    return AnnualPacingAnalysis(
        annual_commitment_budget_mn=annual_commitment_budget_mn,
        reserve_buffer_pct=reserve_buffer_pct,
        points=annual_points,
    )
