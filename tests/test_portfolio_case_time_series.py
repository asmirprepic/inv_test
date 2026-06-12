from altintel.analytics.comparison import compare_portfolio_case_time_series
from altintel.core import load_app_config


def test_portfolio_case_time_series_returns_points_for_all_cases() -> None:
    comparison = compare_portfolio_case_time_series(load_app_config(), commitment_case="infrastructure")

    assert len(comparison.series) >= 4
    assert all(series.points for series in comparison.series)
    assert comparison.series[0].points[-1].holdings_count > 0
