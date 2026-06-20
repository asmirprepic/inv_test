from __future__ import annotations

from altintel.pipeline import run_ai_prospect_ranking_pipeline


def main() -> None:
    result = run_ai_prospect_ranking_pipeline(portfolio_case="balanced_institution")

    print(f"AI prospect ranking for portfolio case: {result.portfolio_case}")
    for prospect in result.prospects[:8]:
        print(
            f"- {prospect.fund_name} | score={prospect.composite_score} | "
            f"strategy={prospect.strategy} | action={prospect.recommended_action}"
        )


if __name__ == "__main__":
    main()
