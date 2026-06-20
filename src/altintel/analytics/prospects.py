from __future__ import annotations

import re

from altintel.core.models import (
    PortfolioSnapshot,
    Prospect,
    ProspectRankingReason,
    ProspectRankingResult,
    ProspectSearchMatch,
    ProspectSearchResult,
    RankedProspect,
)

STOPWORDS = {
    "and",
    "or",
    "with",
    "the",
    "for",
    "high",
    "lower",
    "low",
    "show",
    "find",
    "fund",
    "funds",
}


def _strategy_nav_share(portfolio: PortfolioSnapshot, strategy: str) -> float:
    if portfolio.total_nav_mn == 0:
        return 0.0
    strategy_nav = sum(holding.nav_mn for holding in portfolio.holdings if holding.strategy == strategy)
    return strategy_nav / portfolio.total_nav_mn


def _recommended_action(score: float) -> str:
    if score >= 50:
        return "Advance to next diligence stage."
    if score >= 42:
        return "Keep in active pipeline and test against pacing constraints."
    if score >= 34:
        return "Monitor for better entry timing or clearer differentiation."
    return "Lower near-term priority for allocator bandwidth."


def rank_prospects_for_portfolio(portfolio_case: str, portfolio: PortfolioSnapshot, prospects: list[Prospect]) -> ProspectRankingResult:
    ranked: list[RankedProspect] = []
    for prospect in prospects:
        strategy_share = _strategy_nav_share(portfolio, prospect.strategy)
        reasons: list[ProspectRankingReason] = []

        score = 0.0
        positive_components = {
            "team_quality": prospect.team_score * 2.0,
            "track_record": prospect.track_record_score * 2.2,
            "esg_quality": prospect.esg_score * 1.3,
            "portfolio_fit": prospect.portfolio_fit_score * 2.5,
            "diligence_progress": prospect.dd_score * 1.8,
            "alignment": prospect.gp_commitment_pct * 2.0,
        }
        negative_components = {
            "liquidity_impact": prospect.liquidity_impact_score * 2.1,
            "overlap_risk": prospect.overlap_risk_score * 1.9,
            "management_fee": prospect.management_fee_pct * 6.0,
            "carry": prospect.carry_pct * 0.55,
        }

        for category, component_score in positive_components.items():
            score += component_score
            reasons.append(
                ProspectRankingReason(
                    category=category,
                    score_impact=round(component_score, 4),
                    message=f"{category.replace('_', ' ').title()} supports allocator attractiveness.",
                )
            )
        for category, component_score in negative_components.items():
            score -= component_score
            reasons.append(
                ProspectRankingReason(
                    category=category,
                    score_impact=round(-component_score, 4),
                    message=f"{category.replace('_', ' ').title()} reduces near-term attractiveness.",
                )
            )

        if strategy_share > 0.22:
            concentration_penalty = round((strategy_share - 0.22) * 85.0, 4)
            score -= concentration_penalty
            reasons.append(
                ProspectRankingReason(
                    category="strategy_concentration",
                    score_impact=-concentration_penalty,
                    message="Existing portfolio concentration in this strategy reduces fit.",
                )
            )
        if prospect.proposed_commitment_mn > portfolio.liquid_reserves_mn * 0.45:
            size_penalty = round((prospect.proposed_commitment_mn / portfolio.liquid_reserves_mn) * 10.0, 4)
            score -= size_penalty
            reasons.append(
                ProspectRankingReason(
                    category="commitment_size",
                    score_impact=-size_penalty,
                    message="Proposed ticket size is meaningful relative to liquid reserves.",
                )
            )

        composite_score = round(max(score, 0.0), 4)
        ranked.append(
            RankedProspect(
                prospect_id=prospect.prospect_id,
                fund_name=prospect.fund_name,
                strategy=prospect.strategy,
                geography=prospect.geography,
                status=prospect.status,
                composite_score=composite_score,
                recommended_action=_recommended_action(composite_score),
                reasons=sorted(reasons, key=lambda item: abs(item.score_impact), reverse=True),
            )
        )

    ordered = sorted(ranked, key=lambda item: (-item.composite_score, item.fund_name))
    return ProspectRankingResult(portfolio_case=portfolio_case, prospects=ordered)


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z_]+", text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def search_prospects(query: str, prospects: list[Prospect]) -> ProspectSearchResult:
    query_terms = set(_tokenize(query))
    strategy_aliases = {
        "infra": "infrastructure",
        "forest": "timberland",
        "timber": "timberland",
        "property": "real_estate",
    }
    normalized_terms = set(query_terms)
    for term in list(query_terms):
        if term in strategy_aliases:
            normalized_terms.add(strategy_aliases[term])

    matches: list[ProspectSearchMatch] = []
    for prospect in prospects:
        prospect_terms = set(
            _tokenize(
                " ".join(
                    [
                        prospect.fund_name,
                        prospect.strategy,
                        prospect.geography,
                        prospect.status,
                        " ".join(prospect.tags),
                        prospect.notes,
                    ]
                )
            )
        )
        matched_terms = sorted(normalized_terms & prospect_terms)
        if not matched_terms:
            continue
        base_score = len(matched_terms) * 10.0
        thematic_bonus = prospect.portfolio_fit_score + prospect.dd_score - prospect.overlap_risk_score * 0.4
        match_score = round(base_score + thematic_bonus, 4)
        matches.append(
            ProspectSearchMatch(
                prospect_id=prospect.prospect_id,
                fund_name=prospect.fund_name,
                strategy=prospect.strategy,
                geography=prospect.geography,
                status=prospect.status,
                match_score=match_score,
                matched_terms=matched_terms,
                summary=prospect.notes,
            )
        )

    ordered = sorted(matches, key=lambda item: (-item.match_score, item.fund_name))
    return ProspectSearchResult(query=query, matches=ordered)
