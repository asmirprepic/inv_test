from altintel.pipeline import run_ai_watchlist_pipeline


def test_run_ai_watchlist_pipeline_returns_ranked_entries() -> None:
    result = run_ai_watchlist_pipeline(portfolio_case="balanced_institution", quarters=8, seed=7)

    assert result.entries
    assert result.entries[0].priority_score >= result.entries[-1].priority_score
    assert result.entries[0].priority_label in {"critical", "high", "medium", "low"}
    assert result.entries[0].reasons
