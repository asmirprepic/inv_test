from altintel.cashflows.forecasting import forecast_commitment_cashflows
from altintel.data.sample_data import load_cashflow_assumptions, load_named_proposed_commitment, load_portfolio_snapshot
from altintel.portfolio.pacing import analyze_annual_pacing


def test_analyze_annual_pacing_returns_multi_year_unfunded_path() -> None:
    memo = load_named_proposed_commitment(case_name="infrastructure")
    assumptions = load_cashflow_assumptions()
    portfolio = load_portfolio_snapshot(case_name="balanced_institution")
    forecast = forecast_commitment_cashflows(memo, assumptions["base_case"], portfolio.as_of)

    analysis = analyze_annual_pacing(
        memo=memo,
        forecast=forecast,
        current_unfunded_mn=276.0,
        annual_commitment_budget_mn=180.0,
        reserve_buffer_pct=0.15,
        pacing_years=5,
    )

    assert len(analysis.points) == 5
    assert analysis.points[0].proposed_commitment_mn == 60.0
    assert analysis.points[0].ending_unfunded_mn < 336.0
