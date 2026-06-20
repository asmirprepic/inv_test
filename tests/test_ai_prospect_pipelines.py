from altintel.pipeline import run_ai_prospect_ranking_pipeline, run_ai_prospect_search_pipeline


def test_run_ai_prospect_ranking_pipeline_returns_ranked_prospects() -> None:
    result = run_ai_prospect_ranking_pipeline(portfolio_case="balanced_institution")

    assert len(result.prospects) >= 10
    assert result.prospects[0].composite_score >= result.prospects[-1].composite_score


def test_run_ai_prospect_search_pipeline_returns_matches() -> None:
    result = run_ai_prospect_search_pipeline("Nordic timberland with high esg and low overlap")

    assert result.matches
    assert "timberland" in result.matches[0].strategy or "Nordics" in result.matches[0].geography
