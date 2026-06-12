from __future__ import annotations

from collections import defaultdict
from statistics import mean, pstdev

from altintel.core.models import (
    DataDrivenInsights,
    HoldingAnomalyScore,
    HoldingObservation,
    MonitoringAlert,
    StrategySignal,
)


def _latest_observations(observations: list[HoldingObservation]) -> dict[str, HoldingObservation]:
    latest: dict[str, HoldingObservation] = {}
    for observation in sorted(observations, key=lambda item: item.as_of):
        latest[observation.holding_name] = observation
    return latest


def _group_by_holding(observations: list[HoldingObservation]) -> dict[str, list[HoldingObservation]]:
    grouped: dict[str, list[HoldingObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.holding_name].append(observation)
    return grouped


def _group_by_strategy(observations: list[HoldingObservation]) -> dict[str, list[HoldingObservation]]:
    grouped: dict[str, list[HoldingObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.strategy].append(observation)
    return grouped


def build_strategy_signals(observations: list[HoldingObservation]) -> list[StrategySignal]:
    grouped = _group_by_strategy(observations)
    signals: list[StrategySignal] = []
    for strategy, rows in sorted(grouped.items()):
        nav_series = [row.nav_mn for row in rows]
        distribution_yields = [
            (row.distribution_mn / row.nav_mn) * 100 if row.nav_mn else 0.0
            for row in rows
        ]
        nav_volatility = pstdev(nav_series) / mean(nav_series) * 100 if len(nav_series) > 1 and mean(nav_series) else 0.0
        signals.append(
            StrategySignal(
                strategy=strategy,
                observation_count=len(rows),
                avg_revenue_growth_pct=round(mean(row.revenue_growth_pct for row in rows), 4),
                avg_distribution_yield_pct=round(mean(distribution_yields), 4),
                avg_leverage_ratio=round(mean(row.leverage_ratio for row in rows), 4),
                nav_volatility_pct=round(nav_volatility, 4),
            )
        )
    return signals


def detect_monitoring_alerts(observations: list[HoldingObservation]) -> list[MonitoringAlert]:
    grouped = _group_by_holding(observations)
    alerts: list[MonitoringAlert] = []

    for holding_name, rows in grouped.items():
        ordered = sorted(rows, key=lambda item: item.as_of)
        latest = ordered[-1]
        recent = ordered[-4:] if len(ordered) >= 4 else ordered
        avg_distribution = mean(row.distribution_mn for row in recent)
        avg_leverage = mean(row.leverage_ratio for row in recent)
        avg_valuation = mean(row.valuation_change_pct for row in recent)

        if latest.leverage_ratio - avg_leverage > 0.9:
            alerts.append(
                MonitoringAlert(
                    holding_name=holding_name,
                    as_of=latest.as_of,
                    severity="high",
                    metric="leverage_ratio",
                    message="Latest leverage is materially above the recent trailing average.",
                )
            )
        if avg_distribution > 0 and latest.distribution_mn < avg_distribution * 0.5:
            alerts.append(
                MonitoringAlert(
                    holding_name=holding_name,
                    as_of=latest.as_of,
                    severity="medium",
                    metric="distribution_mn",
                    message="Latest distribution is more than 50% below the recent trailing average.",
                )
            )
        if latest.valuation_change_pct < avg_valuation - 4.0:
            alerts.append(
                MonitoringAlert(
                    holding_name=holding_name,
                    as_of=latest.as_of,
                    severity="high",
                    metric="valuation_change_pct",
                    message="Latest valuation movement is significantly below recent trend.",
                )
            )
        if latest.revenue_growth_pct < 0:
            alerts.append(
                MonitoringAlert(
                    holding_name=holding_name,
                    as_of=latest.as_of,
                    severity="medium",
                    metric="revenue_growth_pct",
                    message="Latest quarter shows negative operating growth.",
                )
            )
    return alerts


def score_holding_anomalies(observations: list[HoldingObservation]) -> list[HoldingAnomalyScore]:
    grouped = _group_by_holding(observations)
    scores: list[HoldingAnomalyScore] = []

    for holding_name, rows in grouped.items():
        ordered = sorted(rows, key=lambda item: item.as_of)
        if len(ordered) < 4:
            continue

        latest = ordered[-1]
        trailing = ordered[-5:-1] if len(ordered) >= 5 else ordered[:-1]

        avg_growth = mean(row.revenue_growth_pct for row in trailing)
        avg_leverage = mean(row.leverage_ratio for row in trailing)
        avg_valuation = mean(row.valuation_change_pct for row in trailing)
        avg_distribution = mean(row.distribution_mn for row in trailing)

        growth_deviation = max(avg_growth - latest.revenue_growth_pct, 0.0)
        leverage_deviation = max(latest.leverage_ratio - avg_leverage, 0.0)
        valuation_deviation = max(avg_valuation - latest.valuation_change_pct, 0.0)
        distribution_deviation = (
            max((avg_distribution - latest.distribution_mn) / avg_distribution, 0.0) if avg_distribution > 0 else 0.0
        )

        anomaly_score = (
            growth_deviation * 1.8
            + leverage_deviation * 10.0
            + valuation_deviation * 1.4
            + distribution_deviation * 18.0
        )
        if anomaly_score >= 22:
            label = "high"
        elif anomaly_score >= 10:
            label = "medium"
        else:
            label = "low"

        scores.append(
            HoldingAnomalyScore(
                holding_name=holding_name,
                strategy=latest.strategy,
                as_of=latest.as_of,
                anomaly_score=round(anomaly_score, 4),
                revenue_growth_deviation=round(growth_deviation, 4),
                leverage_deviation=round(leverage_deviation, 4),
                valuation_deviation=round(valuation_deviation, 4),
                distribution_deviation=round(distribution_deviation, 4),
                label=label,
            )
        )

    return sorted(scores, key=lambda item: (-item.anomaly_score, item.holding_name))


def build_data_driven_insights(observations: list[HoldingObservation], liquid_reserves_mn: float) -> DataDrivenInsights:
    latest = _latest_observations(observations)
    latest_rows = list(latest.values())
    net_cash_burn = sum(row.contribution_mn - row.distribution_mn for row in latest_rows)
    cash_burn_ratio = net_cash_burn / liquid_reserves_mn if liquid_reserves_mn else 0.0

    return DataDrivenInsights(
        observations=observations,
        strategy_signals=build_strategy_signals(observations),
        alerts=detect_monitoring_alerts(observations),
        anomaly_scores=score_holding_anomalies(observations),
        portfolio_cash_burn_ratio=round(cash_burn_ratio, 4),
    )
