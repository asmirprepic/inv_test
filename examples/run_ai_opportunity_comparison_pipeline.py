from __future__ import annotations

from altintel.pipeline import export_ai_opportunity_comparison_pipeline, run_ai_opportunity_comparison_pipeline


def main() -> None:
    compared_ids = [
        "boreal_timberland_iii",
        "water_utilities_ii",
        "northern_midmarket_vi",
    ]
    result = run_ai_opportunity_comparison_pipeline(
        portfolio_case="balanced_institution",
        compared_opportunity_ids=compared_ids,
    )
    artifacts = export_ai_opportunity_comparison_pipeline(
        portfolio_case="balanced_institution",
        compared_opportunity_ids=compared_ids,
    )

    print(result.summary)
    print(f"JSON artifact: {artifacts.json_path}")
    print(f"Markdown artifact: {artifacts.markdown_path}")
    print("Entries:")
    for entry in result.entries:
        print(
            f"- {entry.manager_name} | {entry.fund_name} | score={entry.composite_score} "
            f"| action={entry.recommended_action}"
        )
    print("Dimensions:")
    for dimension in result.dimensions:
        print(
            f"- {dimension.category}: winner={dimension.winner_opportunity_id} "
            f"| diff={dimension.score_difference}"
        )


if __name__ == "__main__":
    main()
