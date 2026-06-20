from __future__ import annotations

from altintel.pipeline import run_ai_prospect_search_pipeline


def main() -> None:
    query = "Nordic timberland or defensive infrastructure with high ESG and lower overlap risk"
    result = run_ai_prospect_search_pipeline(query)

    print(f"AI prospect search query: {result.query}")
    for match in result.matches[:8]:
        print(
            f"- {match.fund_name} | score={match.match_score} | "
            f"matched_terms={match.matched_terms} | summary={match.summary}"
        )


if __name__ == "__main__":
    main()
