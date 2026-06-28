from __future__ import annotations

import _bootstrap

from altintel.analytics.comparison import compare_portfolio_case_time_series
from altintel.core import load_app_config


def main() -> None:
    config = load_app_config()
    comparison = compare_portfolio_case_time_series(config=config, commitment_case="infrastructure")

    print("Quarter-by-quarter comparison for commitment case: infrastructure")
    for series in comparison.series:
        latest = series.points[-1]
        print(
            f"{series.portfolio_case} | quarter={latest.as_of} | nav={latest.total_nav_mn} "
            f"| burn={latest.net_cash_burn_mn} | burn_ratio={latest.cash_burn_ratio} "
            f"| alerts={latest.alert_count}"
        )


if __name__ == "__main__":
    main()
