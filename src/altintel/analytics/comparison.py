from __future__ import annotations

from collections import defaultdict

from altintel.core.models import (
    PortfolioCaseComparison,
    PortfolioCaseTimeSeries,
    PortfolioCaseTimeSeriesPoint,
    PortfolioCasesTimeSeriesComparison,
    PortfolioComparisonResult,
)
from altintel.data.sample_data import list_portfolio_cases
from altintel.pipeline.full_pipeline import run_full_pipeline


def _score_case(result: object) -> float:
    policy_breach_count = sum(1 for check in result.policy_evaluation.checks if check.status == "breach")
    policy_watch_count = sum(1 for check in result.policy_evaluation.checks if check.status == "watch")
    high_severity_alert_count = sum(1 for alert in result.data_driven_insights.alerts if alert.severity == "high")
    alert_count = len(result.data_driven_insights.alerts)

    score = 100.0
    score -= policy_breach_count * 22.0
    score -= policy_watch_count * 8.0
    score -= high_severity_alert_count * 7.0
    score -= max(alert_count - high_severity_alert_count, 0) * 3.0
    score -= result.data_driven_insights.portfolio_cash_burn_ratio * 60.0
    score -= result.portfolio_after.infrastructure_pct_nav * 12.0
    if result.liquidity_stress.breach:
        score -= 25.0
    elif result.liquidity_stress.ending_liquidity_mn < 75.0:
        score -= 10.0
    return round(max(score, 0.0), 2)


def compare_portfolio_cases(config: object, commitment_case: str) -> PortfolioComparisonResult:
    comparisons: list[PortfolioCaseComparison] = []

    for portfolio_case in list_portfolio_cases():
        result = run_full_pipeline(
            config=config,
            portfolio_case=portfolio_case,
            commitment_case=commitment_case,
        )
        policy_breach_count = sum(1 for check in result.policy_evaluation.checks if check.status == "breach")
        policy_watch_count = sum(1 for check in result.policy_evaluation.checks if check.status == "watch")
        high_severity_alert_count = sum(
            1 for alert in result.data_driven_insights.alerts if alert.severity == "high"
        )
        comparisons.append(
            PortfolioCaseComparison(
                portfolio_case=portfolio_case,
                commitment_case=commitment_case,
                suitability_score=_score_case(result),
                policy_breach_count=policy_breach_count,
                policy_watch_count=policy_watch_count,
                monitoring_alert_count=len(result.data_driven_insights.alerts),
                high_severity_alert_count=high_severity_alert_count,
                ending_liquidity_mn=result.liquidity_stress.ending_liquidity_mn,
                liquidity_breach=result.liquidity_stress.breach,
                cash_burn_ratio=result.data_driven_insights.portfolio_cash_burn_ratio,
                concentration_pct_nav=result.portfolio_after.infrastructure_pct_nav,
            )
        )

    ordered = sorted(
        comparisons,
        key=lambda item: (
            -item.suitability_score,
            item.policy_breach_count,
            item.monitoring_alert_count,
            -item.ending_liquidity_mn,
        ),
    )
    return PortfolioComparisonResult(comparisons=ordered)


def compare_portfolio_case_time_series(config: object, commitment_case: str) -> PortfolioCasesTimeSeriesComparison:
    series_collection: list[PortfolioCaseTimeSeries] = []

    for portfolio_case in list_portfolio_cases():
        result = run_full_pipeline(
            config=config,
            portfolio_case=portfolio_case,
            commitment_case=commitment_case,
        )
        observations = result.data_driven_insights.observations
        by_date: dict[object, list[object]] = defaultdict(list)
        for observation in observations:
            by_date[observation.as_of].append(observation)

        points: list[PortfolioCaseTimeSeriesPoint] = []
        for as_of in sorted(by_date):
            rows = by_date[as_of]
            total_nav = sum(row.nav_mn for row in rows)
            total_contributions = sum(row.contribution_mn for row in rows)
            total_distributions = sum(row.distribution_mn for row in rows)
            net_cash_burn = total_contributions - total_distributions
            cash_burn_ratio = (
                net_cash_burn / result.portfolio_after.liquid_reserves_mn if result.portfolio_after.liquid_reserves_mn else 0.0
            )
            alerts_for_date = [alert for alert in result.data_driven_insights.alerts if alert.as_of == as_of]
            high_alerts_for_date = [alert for alert in alerts_for_date if alert.severity == "high"]
            points.append(
                PortfolioCaseTimeSeriesPoint(
                    portfolio_case=portfolio_case,
                    as_of=as_of,
                    holdings_count=len(rows),
                    total_nav_mn=round(total_nav, 4),
                    total_contributions_mn=round(total_contributions, 4),
                    total_distributions_mn=round(total_distributions, 4),
                    net_cash_burn_mn=round(net_cash_burn, 4),
                    cash_burn_ratio=round(cash_burn_ratio, 4),
                    alert_count=len(alerts_for_date),
                    high_severity_alert_count=len(high_alerts_for_date),
                )
            )
        series_collection.append(
            PortfolioCaseTimeSeries(
                portfolio_case=portfolio_case,
                commitment_case=commitment_case,
                points=points,
            )
        )

    return PortfolioCasesTimeSeriesComparison(series=series_collection)
