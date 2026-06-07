from __future__ import annotations

import calendar
from datetime import date

from altintel.core.models import CashflowForecast, CashflowPoint, InvestmentMemoInput


def _add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _annual_curve_to_monthly(curve: list[float]) -> list[float]:
    monthly: list[float] = []
    for annual_rate in curve:
        monthly_rate = annual_rate / 12
        monthly.extend([monthly_rate] * 12)
    return monthly


def forecast_commitment_cashflows(
    memo: InvestmentMemoInput,
    assumptions: dict[str, object],
    start_date: date,
) -> CashflowForecast:
    call_curve = _annual_curve_to_monthly(list(assumptions["call_rate_curve"]))
    distribution_curve = _annual_curve_to_monthly(list(assumptions["distribution_rate_curve"]))
    target_tvpi = float(assumptions["target_tvpi"])

    commitment = memo.commitment_size_mn
    total_target_distributions = commitment * target_tvpi
    cumulative_calls = 0.0
    cumulative_distributions = 0.0
    nav = 0.0
    points: list[CashflowPoint] = []

    horizon = max(len(call_curve), len(distribution_curve))
    for month_index in range(horizon):
        call_rate = call_curve[month_index] if month_index < len(call_curve) else 0.0
        dist_rate = distribution_curve[month_index] if month_index < len(distribution_curve) else 0.0

        contribution = round(commitment * call_rate, 4)
        if cumulative_calls + contribution > commitment:
            contribution = round(max(commitment - cumulative_calls, 0.0), 4)
        cumulative_calls += contribution

        distribution = round(total_target_distributions * dist_rate, 4)
        if cumulative_distributions + distribution > total_target_distributions:
            distribution = round(max(total_target_distributions - cumulative_distributions, 0.0), 4)
        cumulative_distributions += distribution

        # NAV grows with new deployment and declines as capital is returned.
        nav = max(nav + contribution - distribution, 0.0)
        points.append(
            CashflowPoint(
                as_of=_add_months(start_date, month_index + 1),
                contribution_mn=contribution,
                distribution_mn=distribution,
                nav_mn=round(nav, 4),
            )
        )

    if points:
        points[-1].nav_mn = 0.0

    peak_nav_mn = max(point.nav_mn for point in points) if points else 0.0
    dpi = round(cumulative_distributions / commitment, 4) if commitment else 0.0
    residual_nav = points[-1].nav_mn if points else 0.0
    tvpi = round((cumulative_distributions + residual_nav) / commitment, 4) if commitment else 0.0
    return CashflowForecast(
        fund_name=memo.fund_name,
        forecast_points=points,
        peak_nav_mn=round(peak_nav_mn, 4),
        dpi=dpi,
        tvpi=tvpi,
    )
