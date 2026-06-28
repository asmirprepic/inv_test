from __future__ import annotations

import _bootstrap

from altintel.core import load_app_config
from altintel.pipeline.full_pipeline import run_full_pipeline


def main() -> None:
    result = run_full_pipeline(load_app_config(), portfolio_case="balanced_institution", commitment_case="infrastructure")

    print("Annual commitment pacing view")
    print(f"Budget (EUR mn): {result.annual_pacing.annual_commitment_budget_mn}")
    for point in result.annual_pacing.points:
        print(
            f"{point.year} | proposed={point.proposed_commitment_mn} | calls={point.called_capital_mn} "
            f"| dists={point.distributions_mn} | net={point.net_cash_outflow_mn} "
            f"| unfunded={point.ending_unfunded_mn} | reserve_buffer={point.reserve_buffer_mn}"
        )


if __name__ == "__main__":
    main()
