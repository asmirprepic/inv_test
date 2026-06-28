from __future__ import annotations

import _bootstrap

from altintel.analytics.monitoring import build_data_driven_insights
from altintel.data.sample_data import load_portfolio_snapshot
from altintel.data.simulation import export_monitoring_data, generate_portfolio_monitoring_data


def main() -> None:
    portfolio = load_portfolio_snapshot(case_name="balanced_institution")
    observations = generate_portfolio_monitoring_data(portfolio, quarters=12, seed=11)
    insights = build_data_driven_insights(observations, portfolio.liquid_reserves_mn)
    export_path = "outputs/simulated_monitoring_balanced_institution.json"
    export_monitoring_data(observations, export_path)

    print(f"Generated observations: {len(observations)}")
    print(f"Exported dataset: {export_path}")
    print(f"Monitoring alerts: {len(insights.alerts)}")
    for alert in insights.alerts[:5]:
        print(f"- {alert.holding_name} | {alert.metric} | {alert.severity}")


if __name__ == "__main__":
    main()
