from pathlib import Path

from altintel.core import load_app_config
from altintel.pipeline import (
    export_ai_commitment_recommendation_pipeline,
    export_ai_opportunity_comparison_pipeline,
    export_ai_opportunity_ranking_pipeline,
    export_denominator_effect_pipeline,
)


def test_export_ai_opportunity_artifacts(tmp_path: Path) -> None:
    ranking = export_ai_opportunity_ranking_pipeline(
        portfolio_case="balanced_institution",
        output_dir=tmp_path,
    )
    comparison = export_ai_opportunity_comparison_pipeline(
        portfolio_case="balanced_institution",
        compared_opportunity_ids=["boreal_timberland_iii", "water_utilities_ii"],
        output_dir=tmp_path,
    )
    recommendation = export_ai_commitment_recommendation_pipeline(
        portfolio_case="balanced_institution",
        opportunity_id="water_utilities_ii",
        output_dir=tmp_path,
    )
    denominator = export_denominator_effect_pipeline(
        load_app_config(),
        portfolio_case="balanced_institution",
        output_dir=tmp_path,
    )

    assert ranking.json_path.exists()
    assert ranking.markdown_path.exists()
    assert comparison.json_path.exists()
    assert comparison.markdown_path.exists()
    assert recommendation.json_path.exists()
    assert recommendation.markdown_path.exists()
    assert denominator.json_path.exists()
    assert denominator.markdown_path.exists()
