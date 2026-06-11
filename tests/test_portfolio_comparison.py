from altintel.analytics.comparison import compare_portfolio_cases
from altintel.core import load_app_config


def test_compare_portfolio_cases_returns_ranked_results() -> None:
    result = compare_portfolio_cases(load_app_config(), commitment_case="infrastructure")

    assert len(result.comparisons) >= 4
    assert result.comparisons[0].suitability_score >= result.comparisons[-1].suitability_score
    assert {item.portfolio_case for item in result.comparisons} >= {
        "balanced_institution",
        "infra_overweight",
        "liquidity_constrained",
        "real_assets_heavy",
    }
