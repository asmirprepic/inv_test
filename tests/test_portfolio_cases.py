from altintel.data.sample_data import (
    list_commitment_cases,
    list_portfolio_cases,
    load_named_proposed_commitment,
    load_portfolio_snapshot,
)


def test_list_portfolio_cases_contains_new_scenarios() -> None:
    cases = list_portfolio_cases()

    assert "balanced_institution" in cases
    assert "infra_overweight" in cases
    assert "real_assets_heavy" in cases
    assert "liquidity_constrained" in cases


def test_load_named_portfolio_case() -> None:
    portfolio = load_portfolio_snapshot(case_name="liquidity_constrained")

    assert portfolio.total_nav_mn == 760.0
    assert portfolio.liquid_reserves_mn == 62.0
    assert len(portfolio.holdings) == 7


def test_named_commitment_cases_include_timberland() -> None:
    cases = list_commitment_cases()
    memo = load_named_proposed_commitment(case_name="timberland")

    assert "timberland" in cases
    assert memo.strategy == "timberland"
    assert memo.commitment_size_mn == 45.0
