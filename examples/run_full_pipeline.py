from __future__ import annotations

from altintel.core import load_app_config
from altintel.pipeline.full_pipeline import run_full_pipeline


def main() -> None:
    config = load_app_config()
    result = run_full_pipeline(config)

    print(f"Fund: {result.due_diligence.facts.fund_name}")
    print(f"Overall risk rating: {result.due_diligence.overall_risk_rating}")
    print(f"Portfolio NAV before commitment (EUR mn): {result.portfolio_before.total_nav_mn}")
    print(f"Portfolio unfunded before commitment (EUR mn): {result.portfolio_before.total_unfunded_mn}")
    print(f"Portfolio unfunded after commitment (EUR mn): {result.portfolio_after.total_unfunded_mn}")
    print(f"Base case peak NAV (EUR mn): {result.base_case_peak_nav_mn}")
    print(f"Base case DPI: {result.base_case_dpi}")
    print(f"Base case TVPI: {result.base_case_tvpi}")
    print(f"Downside peak NAV (EUR mn): {result.downside_case_peak_nav_mn}")
    print(f"Downside TVPI: {result.downside_case_tvpi}")
    print(f"Stress ending liquidity (EUR mn): {result.liquidity_stress.ending_liquidity_mn}")
    print(f"Stress breach: {result.liquidity_stress.breach}")
    print("Policy checks:")
    for check in result.policy_evaluation.checks:
        print(
            f"- {check.name}: {check.status} | metric={check.metric_value} threshold={check.threshold_value}"
        )
    print(f"Monitoring alerts: {len(result.data_driven_insights.alerts)}")
    print(f"Portfolio cash burn ratio: {result.data_driven_insights.portfolio_cash_burn_ratio}")
    print("Top anomaly scores:")
    for anomaly in result.data_driven_insights.anomaly_scores[:3]:
        print(
            f"- {anomaly.holding_name}: score={anomaly.anomaly_score} "
            f"label={anomaly.label} leverage_dev={anomaly.leverage_deviation}"
        )
    print("Strategy signals:")
    for signal in result.data_driven_insights.strategy_signals:
        print(
            f"- {signal.strategy}: growth={signal.avg_revenue_growth_pct}% "
            f"yield={signal.avg_distribution_yield_pct}% leverage={signal.avg_leverage_ratio}"
        )


if __name__ == "__main__":
    main()
