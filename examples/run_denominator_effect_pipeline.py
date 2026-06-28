from __future__ import annotations

import _bootstrap

from altintel.core import load_app_config
from altintel.pipeline import export_denominator_effect_pipeline, run_denominator_effect_pipeline


def main() -> None:
    result = run_denominator_effect_pipeline(
        load_app_config(),
        portfolio_case="balanced_institution",
        public_market_drawdown_pct=0.25,
    )
    artifacts = export_denominator_effect_pipeline(
        load_app_config(),
        portfolio_case="balanced_institution",
        public_market_drawdown_pct=0.25,
    )

    print(result.summary)
    print(f"JSON artifact: {artifacts.json_path}")
    print(f"Markdown artifact: {artifacts.markdown_path}")
    print(f"Target private-markets pct: {result.target_private_markets_pct}")
    print(f"Overweight gap pct: {result.overweight_gap_pct}")
    print(f"Stressed liquid reserves (EUR mn): {result.stressed_liquid_reserves_mn}")
    print("Top stressed opportunity impacts:")
    for impact in result.opportunity_impacts[:6]:
        print(
            f"- {impact.manager_name} | {impact.fund_name} | base={impact.base_composite_score} "
            f"| stressed={impact.stressed_composite_score} | rec={impact.stressed_recommendation} "
            f"| constraint={impact.key_constraint}"
        )


if __name__ == "__main__":
    main()
