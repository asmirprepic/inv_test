from __future__ import annotations

import _bootstrap

from altintel.core import load_app_config
from altintel.pipeline import (
    export_ai_commitment_recommendation_pipeline,
    run_ai_commitment_recommendation_pipeline,
)


def main() -> None:
    config = load_app_config()
    result = run_ai_commitment_recommendation_pipeline(
        portfolio_case="balanced_institution",
        opportunity_id="water_utilities_ii",
        config=config,
        public_market_drawdown_pct=0.25,
    )
    artifacts = export_ai_commitment_recommendation_pipeline(
        portfolio_case="balanced_institution",
        opportunity_id="water_utilities_ii",
        config=config,
        public_market_drawdown_pct=0.25,
    )

    print(result.summary)
    print(f"JSON artifact: {artifacts.json_path}")
    print(f"Markdown artifact: {artifacts.markdown_path}")
    print(f"Recommendation: {result.recommendation}")
    print(f"Baseline recommendation: {result.baseline_recommendation}")
    print(f"Stressed private-markets pct: {result.stressed_private_markets_pct}")
    print(f"Key stressed constraint: {result.stressed_key_constraint}")


if __name__ == "__main__":
    main()
