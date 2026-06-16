from __future__ import annotations

from collections import defaultdict

from altintel.core.models import (
    AIWatchlistResult,
    DataDrivenInsights,
    HoldingObservation,
    WatchlistEntry,
    WatchlistReason,
)


def _latest_observation_map(observations: list[HoldingObservation]) -> dict[str, HoldingObservation]:
    latest: dict[str, HoldingObservation] = {}
    for observation in sorted(observations, key=lambda item: item.as_of):
        latest[observation.holding_name] = observation
    return latest


def _alerts_by_holding(insights: DataDrivenInsights) -> dict[str, list[object]]:
    grouped: dict[str, list[object]] = defaultdict(list)
    for alert in insights.alerts:
        grouped[alert.holding_name].append(alert)
    return grouped


def _strategy_volatility_map(insights: DataDrivenInsights) -> dict[str, float]:
    return {signal.strategy: signal.nav_volatility_pct for signal in insights.strategy_signals}


def _priority_label(score: float) -> str:
    if score >= 32:
        return "critical"
    if score >= 20:
        return "high"
    if score >= 10:
        return "medium"
    return "low"


def _recommended_action(label: str) -> str:
    if label == "critical":
        return "Escalate to quarterly watchlist review and request manager follow-up."
    if label == "high":
        return "Add to active watchlist and review next reporting cycle."
    if label == "medium":
        return "Monitor closely for another quarter before escalation."
    return "No immediate escalation required."


def build_ai_watchlist(portfolio_case: str, insights: DataDrivenInsights) -> AIWatchlistResult:
    latest_map = _latest_observation_map(insights.observations)
    alerts_map = _alerts_by_holding(insights)
    volatility_map = _strategy_volatility_map(insights)
    anomaly_map = {score.holding_name: score for score in insights.anomaly_scores}
    generated_as_of = max(observation.as_of for observation in insights.observations)

    entries: list[WatchlistEntry] = []
    for holding_name, latest in latest_map.items():
        anomaly = anomaly_map.get(holding_name)
        if anomaly is None:
            continue
        alerts = alerts_map.get(holding_name, [])
        strategy_volatility = volatility_map.get(latest.strategy, 0.0)

        score = anomaly.anomaly_score
        reasons: list[WatchlistReason] = []

        if anomaly.leverage_deviation > 0:
            strength = round(anomaly.leverage_deviation * 10.0, 4)
            score += strength
            reasons.append(
                WatchlistReason(
                    category="leverage",
                    signal_strength=strength,
                    message="Leverage has moved above the recent trailing baseline.",
                )
            )
        if anomaly.valuation_deviation > 0:
            strength = round(anomaly.valuation_deviation * 1.2, 4)
            score += strength
            reasons.append(
                WatchlistReason(
                    category="valuation",
                    signal_strength=strength,
                    message="Valuation trend has weakened relative to recent quarters.",
                )
            )
        if anomaly.distribution_deviation > 0:
            strength = round(anomaly.distribution_deviation * 12.0, 4)
            score += strength
            reasons.append(
                WatchlistReason(
                    category="distributions",
                    signal_strength=strength,
                    message="Distribution profile is below its recent run-rate.",
                )
            )
        if latest.revenue_growth_pct < 0:
            strength = round(abs(latest.revenue_growth_pct) * 0.8, 4)
            score += strength
            reasons.append(
                WatchlistReason(
                    category="operating_growth",
                    signal_strength=strength,
                    message="Latest quarter shows negative operating growth.",
                )
            )
        if strategy_volatility > 18:
            strength = round((strategy_volatility - 18) * 0.5, 4)
            score += strength
            reasons.append(
                WatchlistReason(
                    category="strategy_volatility",
                    signal_strength=strength,
                    message="The broader strategy peer group is showing elevated NAV volatility.",
                )
            )

        for alert in alerts:
            strength = 8.0 if alert.severity == "high" else 4.0
            score += strength
            reasons.append(
                WatchlistReason(
                    category=str(alert.metric),
                    signal_strength=strength,
                    message=str(alert.message),
                )
            )

        if insights.portfolio_cash_burn_ratio > 0.12:
            strength = round((insights.portfolio_cash_burn_ratio - 0.12) * 30.0, 4)
            score += max(strength, 0.0)
            reasons.append(
                WatchlistReason(
                    category="portfolio_liquidity_context",
                    signal_strength=max(strength, 0.0),
                    message="Portfolio cash burn context increases the priority of operational underperformers.",
                )
            )

        priority_score = round(score, 4)
        priority_label = _priority_label(priority_score)
        entries.append(
            WatchlistEntry(
                holding_name=holding_name,
                strategy=latest.strategy,
                as_of=latest.as_of,
                priority_score=priority_score,
                priority_label=priority_label,
                recommended_action=_recommended_action(priority_label),
                reasons=sorted(reasons, key=lambda item: -item.signal_strength),
            )
        )

    ordered_entries = sorted(entries, key=lambda item: (-item.priority_score, item.holding_name))
    return AIWatchlistResult(
        portfolio_case=portfolio_case,
        generated_as_of=generated_as_of,
        portfolio_cash_burn_ratio=insights.portfolio_cash_burn_ratio,
        entries=ordered_entries,
    )
