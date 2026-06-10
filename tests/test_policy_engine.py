from altintel.core import load_app_config
from altintel.data.sample_data import load_named_proposed_commitment, load_portfolio_snapshot
from altintel.cashflows.forecasting import forecast_commitment_cashflows
from altintel.data.sample_data import load_cashflow_assumptions
from altintel.portfolio.analysis import add_proposed_commitment
from altintel.portfolio.policy import evaluate_portfolio_policy


def test_policy_engine_returns_named_checks() -> None:
    config = load_app_config()
    memo = load_named_proposed_commitment(case_name="infrastructure")
    portfolio = add_proposed_commitment(load_portfolio_snapshot(case_name="balanced_institution"), memo)
    assumptions = load_cashflow_assumptions()
    forecast = forecast_commitment_cashflows(memo, assumptions["downside_case"], portfolio.as_of)

    evaluation = evaluate_portfolio_policy(
        portfolio=portfolio,
        proposed_commitment=memo,
        forecast=forecast,
        policy=config.portfolio_policy["policy"],
    )

    check_names = {check.name for check in evaluation.checks}
    assert "max_single_fund_pct_nav" in check_names
    assert "min_liquidity_coverage_months" in check_names
    assert "target_private_markets_pct" in check_names
