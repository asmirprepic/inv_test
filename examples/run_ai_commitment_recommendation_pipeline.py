from __future__ import annotations

from altintel.pipeline import (
    export_ai_commitment_recommendation_pipeline,
    run_ai_commitment_recommendation_pipeline,
)


def main() -> None:
    result = run_ai_commitment_recommendation_pipeline(
        portfolio_case="balanced_institution",
        opportunity_id="water_utilities_ii",
    )
    artifacts = export_ai_commitment_recommendation_pipeline(
        portfolio_case="balanced_institution",
        opportunity_id="water_utilities_ii",
    )

    print(result.summary)
    print(f"JSON artifact: {artifacts.json_path}")
    print(f"Markdown artifact: {artifacts.markdown_path}")
    print(f"Recommendation: {result.recommendation}")
    print(f"Conviction: {result.conviction}")
    print(f"Composite score: {result.composite_score}")
    print("Reasons:")
    for reason in result.reasons:
        print(f"- {reason.category} | {reason.impact} | {reason.message}")
    print("Conditions:")
    for condition in result.conditions:
        print(f"- {condition}")


if __name__ == "__main__":
    main()
