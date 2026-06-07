from __future__ import annotations

from altintel.core.models import InvestmentMemoInput, PortfolioHolding, PortfolioSnapshot, PortfolioSummary


def summarize_portfolio(snapshot: PortfolioSnapshot) -> PortfolioSummary:
    total_unfunded = sum(holding.unfunded_mn for holding in snapshot.holdings)
    infrastructure_nav = sum(
        holding.nav_mn for holding in snapshot.holdings if holding.strategy == "infrastructure"
    )
    infrastructure_pct_nav = infrastructure_nav / snapshot.total_nav_mn if snapshot.total_nav_mn else 0.0
    return PortfolioSummary(
        total_nav_mn=snapshot.total_nav_mn,
        total_unfunded_mn=round(total_unfunded, 4),
        liquid_reserves_mn=snapshot.liquid_reserves_mn,
        infrastructure_nav_mn=round(infrastructure_nav, 4),
        infrastructure_pct_nav=round(infrastructure_pct_nav, 4),
    )


def add_proposed_commitment(snapshot: PortfolioSnapshot, memo: InvestmentMemoInput) -> PortfolioSnapshot:
    updated_holdings = list(snapshot.holdings)
    updated_holdings.append(
        PortfolioHolding(
            name=memo.fund_name,
            strategy=memo.strategy,
            nav_mn=0.0,
            unfunded_mn=memo.commitment_size_mn,
        )
    )
    return PortfolioSnapshot(
        as_of=snapshot.as_of,
        total_nav_mn=snapshot.total_nav_mn,
        liquid_reserves_mn=snapshot.liquid_reserves_mn,
        holdings=updated_holdings,
    )
