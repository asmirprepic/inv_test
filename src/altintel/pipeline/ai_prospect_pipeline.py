from __future__ import annotations

from dataclasses import dataclass

from altintel.analytics.prospects import (
    compare_opportunities,
    rank_opportunities_for_portfolio,
    recommend_commitment,
    search_opportunities,
)
from altintel.core import (
    CommitmentRecommendationResult,
    OpportunityComparisonResult,
    OpportunityRankingResult,
    OpportunitySearchResult,
    PortfolioSnapshot,
)
from altintel.data.sample_data import load_opportunity_registry, load_portfolio_snapshot


@dataclass(slots=True)
class AIOpportunityUniverse:
    portfolio_case: str
    portfolio: PortfolioSnapshot
    opportunity_count: int


def build_ai_opportunity_universe(portfolio_case: str = "balanced_institution") -> AIOpportunityUniverse:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    opportunities = load_opportunity_registry()
    return AIOpportunityUniverse(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunity_count=len(opportunities),
    )


def run_ai_opportunity_ranking_pipeline(portfolio_case: str = "balanced_institution") -> OpportunityRankingResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    opportunities = load_opportunity_registry()
    return rank_opportunities_for_portfolio(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunities=opportunities,
    )


def run_ai_opportunity_search_pipeline(query: str) -> OpportunitySearchResult:
    opportunities = load_opportunity_registry()
    return search_opportunities(query=query, opportunities=opportunities)


def run_ai_opportunity_comparison_pipeline(
    portfolio_case: str,
    compared_opportunity_ids: list[str],
) -> OpportunityComparisonResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    opportunities = load_opportunity_registry()
    return compare_opportunities(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunities=opportunities,
        compared_opportunity_ids=compared_opportunity_ids,
    )


def run_ai_commitment_recommendation_pipeline(
    portfolio_case: str,
    opportunity_id: str,
) -> CommitmentRecommendationResult:
    portfolio = load_portfolio_snapshot(case_name=portfolio_case)
    opportunities = load_opportunity_registry()
    return recommend_commitment(
        portfolio_case=portfolio_case,
        portfolio=portfolio,
        opportunities=opportunities,
        opportunity_id=opportunity_id,
    )
