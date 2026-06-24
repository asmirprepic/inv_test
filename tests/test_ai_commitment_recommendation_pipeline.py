from altintel.pipeline import run_ai_commitment_recommendation_pipeline


def test_run_ai_commitment_recommendation_pipeline_returns_recommendation() -> None:
    result = run_ai_commitment_recommendation_pipeline(
        portfolio_case="balanced_institution",
        opportunity_id="water_utilities_ii",
    )

    assert result.recommendation in {"advance", "advance_with_conditions", "hold", "decline"}
    assert result.conviction in {"high", "medium", "low"}
    assert result.reasons
