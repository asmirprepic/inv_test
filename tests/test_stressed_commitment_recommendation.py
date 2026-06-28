from altintel.core import load_app_config
from altintel.pipeline import run_ai_commitment_recommendation_pipeline


def test_run_ai_commitment_recommendation_pipeline_with_denominator_effect() -> None:
    result = run_ai_commitment_recommendation_pipeline(
        portfolio_case="balanced_institution",
        opportunity_id="water_utilities_ii",
        config=load_app_config(),
        public_market_drawdown_pct=0.25,
    )

    assert result.denominator_effect_applied is True
    assert result.baseline_recommendation is not None
    assert result.stressed_private_markets_pct is not None
    assert result.stressed_key_constraint is not None
