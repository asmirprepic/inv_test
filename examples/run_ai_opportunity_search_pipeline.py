from __future__ import annotations

from altintel.pipeline import run_ai_opportunity_search_pipeline


def main() -> None:
    query = "Nordic re-up or timberland primary with good pacing fit and lower overlap"
    result = run_ai_opportunity_search_pipeline(query)

    print(f"AI opportunity search query: {result.query}")
    for match in result.matches[:8]:
        print(
            f"- {match.manager_name} | {match.fund_name} | score={match.match_score} | "
            f"vehicle={match.vehicle_type} | stage={match.pipeline_stage} | matched_terms={match.matched_terms}"
        )


if __name__ == "__main__":
    main()
