from altintel.pipeline import run_ai_opportunity_ranking_pipeline, run_ai_opportunity_search_pipeline


def test_run_ai_opportunity_ranking_pipeline_returns_ranked_opportunities() -> None:
    result = run_ai_opportunity_ranking_pipeline(portfolio_case="balanced_institution")

    assert len(result.opportunities) >= 8
    assert result.opportunities[0].composite_score >= result.opportunities[-1].composite_score


def test_run_ai_opportunity_search_pipeline_returns_matches() -> None:
    result = run_ai_opportunity_search_pipeline("Nordic re-up or timberland primary with low overlap")

    assert result.matches
    assert result.matches[0].vehicle_type in {"primary", "re_up", "co_invest"}
