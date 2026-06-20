from __future__ import annotations

from dataclasses import dataclass

from altintel.analytics.prospects import rank_prospects_for_portfolio, search_prospects
from altintel.core import PortfolioSnapshot, ProspectRankingResult, ProspectSearchResult
from altintel.data.sample_data import load_portfolio_snapshot, load_prospect_registry


@dataclass(slots=True)
class AIProspectUniverse:
    portfolio_case: str
    portfolio: PortfolioSnapshot
    prospect_count: int


def build_ai_prospect_universe(portfolio_case: str = "balanced_institution") -> AIProspectUniverse:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    prospects = load_prospect_registry()
    return AIProspectUniverse(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        prospect_count=len(prospects),
    )


def run_ai_prospect_ranking_pipeline(portfolio_case: str = "balanced_institution") -> ProspectRankingResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    prospects = load_prospect_registry()
    return rank_prospects_for_portfolio(portfolio_case=portfolio_case, portfolio=portfolio, prospects=prospects)


def run_ai_prospect_search_pipeline(query: str) -> ProspectSearchResult:
    prospects = load_prospect_registry()
    return search_prospects(query=query, prospects=prospects)
