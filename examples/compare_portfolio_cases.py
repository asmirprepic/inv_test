from __future__ import annotations

import _bootstrap

from altintel.analytics.comparison import compare_portfolio_cases
from altintel.core import load_app_config


def main() -> None:
    config = load_app_config()
    result = compare_portfolio_cases(config=config, commitment_case="infrastructure")

    print("Portfolio case ranking for commitment case: infrastructure")
    for index, comparison in enumerate(result.comparisons, start=1):
        print(
            f"{index}. {comparison.portfolio_case} | score={comparison.suitability_score} "
            f"| breaches={comparison.policy_breach_count} | alerts={comparison.monitoring_alert_count} "
            f"| ending_liquidity={comparison.ending_liquidity_mn}"
        )


if __name__ == "__main__":
    main()
