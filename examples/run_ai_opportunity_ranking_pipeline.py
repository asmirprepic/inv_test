from __future__ import annotations

import _bootstrap

from altintel.pipeline import export_ai_opportunity_ranking_pipeline, run_ai_opportunity_ranking_pipeline


def main() -> None:
    result = run_ai_opportunity_ranking_pipeline(portfolio_case="balanced_institution")
    artifacts = export_ai_opportunity_ranking_pipeline(portfolio_case="balanced_institution")

    print(f"AI opportunity ranking for portfolio case: {result.portfolio_case}")
    print(f"JSON artifact: {artifacts.json_path}")
    print(f"Markdown artifact: {artifacts.markdown_path}")
    for opportunity in result.opportunities[:8]:
        print(
            f"- {opportunity.manager_name} | {opportunity.fund_name} | score={opportunity.composite_score} | "
            f"vehicle={opportunity.vehicle_type} | stage={opportunity.pipeline_stage} | action={opportunity.recommended_action}"
        )


if __name__ == "__main__":
    main()
