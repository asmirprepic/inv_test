from altintel.pipeline import run_ai_opportunity_comparison_pipeline


def test_run_ai_opportunity_comparison_pipeline_returns_preferred_opportunity() -> None:
    result = run_ai_opportunity_comparison_pipeline(
        portfolio_case="balanced_institution",
        compared_opportunity_ids=[
            "boreal_timberland_iii",
            "water_utilities_ii",
            "northern_midmarket_vi",
        ],
    )

    assert result.preferred_opportunity_id is not None
    assert len(result.entries) == 3
    assert result.dimensions
