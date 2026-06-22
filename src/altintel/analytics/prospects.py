from __future__ import annotations

import re

from altintel.core.models import (
    CommitmentRecommendationReason,
    CommitmentRecommendationResult,
    InvestmentOpportunity,
    OpportunityComparisonDimension,
    OpportunityComparisonEntry,
    OpportunityComparisonResult,
    OpportunityRankingReason,
    OpportunityRankingResult,
    OpportunitySearchMatch,
    OpportunitySearchResult,
    PortfolioSnapshot,
    RankedOpportunity,
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
    "good",
    "fit",
}


def _strategy_nav_share(portfolio: PortfolioSnapshot, strategy: str) -> float:
    if portfolio.total_nav_mn == 0:
        return 0.0
    strategy_nav = sum(holding.nav_mn for holding in portfolio.holdings if holding.strategy == strategy)
    return strategy_nav / portfolio.total_nav_mn


def _recommended_action(score: float, stage: str, existing_gp_relationship: bool, vehicle_type: str) -> str:
    if vehicle_type == "re_up" and score >= 44:
        return "Prepare re-up recommendation with updated portfolio-fit analysis."
    if stage == "dd" and score >= 48:
        return "Advance toward investment committee review."
    if score >= 44:
        return "Advance to next diligence stage."
    if score >= 36:
        return "Keep in active pipeline and test against pacing constraints."
    if existing_gp_relationship and score >= 30:
        return "Hold for relationship review and selective follow-up."
    return "Lower near-term priority for allocator bandwidth."


def rank_opportunities_for_portfolio(
    portfolio_case: str,
    portfolio: PortfolioSnapshot,
    opportunities: list[InvestmentOpportunity],
) -> OpportunityRankingResult:
    ranked: list[RankedOpportunity] = []
    for opportunity in opportunities:
        strategy_share = _strategy_nav_share(portfolio, opportunity.strategy)
        reasons: list[OpportunityRankingReason] = []

        score = 0.0
        positive_components = {
            "team_quality": opportunity.team_score * 2.0,
            "track_record": opportunity.track_record_score * 2.2,
            "esg_quality": opportunity.esg_score * 1.3,
            "portfolio_fit": opportunity.portfolio_fit_score * 2.6,
            "diligence_progress": opportunity.dd_score * 1.9,
            "alignment": opportunity.gp_commitment_pct * 2.0,
            "pacing_slot": opportunity.pacing_slot_score * 2.1,
        }
        negative_components = {
            "liquidity_impact": opportunity.liquidity_impact_score * 2.1,
            "overlap_risk": opportunity.overlap_risk_score * 2.0,
            "management_fee": opportunity.management_fee_pct * 6.0,
            "carry": opportunity.carry_pct * 0.55,
        }

        for category, component_score in positive_components.items():
            score += component_score
            reasons.append(
                OpportunityRankingReason(
                    category=category,
                    score_impact=round(component_score, 4),
                    message=f"{category.replace('_', ' ').title()} supports allocator attractiveness.",
                )
            )
        for category, component_score in negative_components.items():
            score -= component_score
            reasons.append(
                OpportunityRankingReason(
                    category=category,
                    score_impact=round(-component_score, 4),
                    message=f"{category.replace('_', ' ').title()} reduces near-term attractiveness.",
                )
            )

        if strategy_share > 0.22:
            concentration_penalty = round((strategy_share - 0.22) * 85.0, 4)
            score -= concentration_penalty
            reasons.append(
                OpportunityRankingReason(
                    category="strategy_concentration",
                    score_impact=-concentration_penalty,
                    message="Existing portfolio concentration in this strategy reduces fit.",
                )
            )
        if opportunity.proposed_commitment_mn > portfolio.liquid_reserves_mn * 0.45:
            size_penalty = round((opportunity.proposed_commitment_mn / portfolio.liquid_reserves_mn) * 10.0, 4)
            score -= size_penalty
            reasons.append(
                OpportunityRankingReason(
                    category="commitment_size",
                    score_impact=-size_penalty,
                    message="Proposed ticket size is meaningful relative to liquid reserves.",
                )
            )
        if opportunity.existing_gp_relationship:
            relationship_bonus = 4.5
            score += relationship_bonus
            reasons.append(
                OpportunityRankingReason(
                    category="existing_gp_relationship",
                    score_impact=relationship_bonus,
                    message="Existing GP relationship improves diligence efficiency and conviction.",
                )
            )
        if opportunity.od_diligence_status == "completed":
            od_bonus = 3.0
            score += od_bonus
            reasons.append(
                OpportunityRankingReason(
                    category="operational_diligence",
                    score_impact=od_bonus,
                    message="Operational diligence is already completed.",
                )
            )
        if opportunity.expected_call_profile == "fast":
            fast_call_penalty = 5.0
            score -= fast_call_penalty
            reasons.append(
                OpportunityRankingReason(
                    category="call_profile",
                    score_impact=-fast_call_penalty,
                    message="Fast call profile tightens pacing flexibility.",
                )
            )

        composite_score = round(max(score, 0.0), 4)
        ranked.append(
            RankedOpportunity(
                opportunity_id=opportunity.opportunity_id,
                manager_name=opportunity.manager_name,
                fund_name=opportunity.fund_name,
                strategy=opportunity.strategy,
                vehicle_type=opportunity.vehicle_type,
                geography=opportunity.geography,
                pipeline_stage=opportunity.pipeline_stage,
                composite_score=composite_score,
                recommended_action=_recommended_action(
                    composite_score,
                    opportunity.pipeline_stage,
                    opportunity.existing_gp_relationship,
                    opportunity.vehicle_type,
                ),
                reasons=sorted(reasons, key=lambda item: abs(item.score_impact), reverse=True),
            )
        )

    ordered = sorted(ranked, key=lambda item: (-item.composite_score, item.fund_name))
    return OpportunityRankingResult(portfolio_case=portfolio_case, opportunities=ordered)


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z_]+", text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def search_opportunities(query: str, opportunities: list[InvestmentOpportunity]) -> OpportunitySearchResult:
    query_terms = set(_tokenize(query))
    strategy_aliases = {
        "infra": "infrastructure",
        "forest": "timberland",
        "timber": "timberland",
        "property": "real_estate",
        "reup": "re_up",
        "coinvest": "co_invest",
    }
    normalized_terms = set(query_terms)
    for term in list(query_terms):
        if term in strategy_aliases:
            normalized_terms.add(strategy_aliases[term])

    matches: list[OpportunitySearchMatch] = []
    for opportunity in opportunities:
        opportunity_terms = set(
            _tokenize(
                " ".join(
                    [
                        opportunity.manager_name,
                        opportunity.fund_name,
                        opportunity.strategy,
                        opportunity.vehicle_type,
                        opportunity.geography,
                        opportunity.pipeline_stage,
                        opportunity.target_strategy_bucket,
                        opportunity.od_diligence_status,
                        opportunity.legal_status,
                        " ".join(opportunity.tags),
                        opportunity.portfolio_overlap_notes,
                    ]
                )
            )
        )
        matched_terms = sorted(normalized_terms & opportunity_terms)
        if not matched_terms:
            continue
        base_score = len(matched_terms) * 10.0
        thematic_bonus = (
            opportunity.portfolio_fit_score
            + opportunity.dd_score
            + opportunity.pacing_slot_score * 0.5
            - opportunity.overlap_risk_score * 0.4
        )
        match_score = round(base_score + thematic_bonus, 4)
        matches.append(
            OpportunitySearchMatch(
                opportunity_id=opportunity.opportunity_id,
                manager_name=opportunity.manager_name,
                fund_name=opportunity.fund_name,
                strategy=opportunity.strategy,
                vehicle_type=opportunity.vehicle_type,
                geography=opportunity.geography,
                pipeline_stage=opportunity.pipeline_stage,
                match_score=match_score,
                matched_terms=matched_terms,
                summary=opportunity.portfolio_overlap_notes,
            )
        )

    ordered = sorted(matches, key=lambda item: (-item.match_score, item.fund_name))
    return OpportunitySearchResult(query=query, matches=ordered)


def compare_opportunities(
    portfolio_case: str,
    portfolio: PortfolioSnapshot,
    opportunities: list[InvestmentOpportunity],
    compared_opportunity_ids: list[str],
) -> OpportunityComparisonResult:
    selected = [opportunity for opportunity in opportunities if opportunity.opportunity_id in compared_opportunity_ids]
    ranking = rank_opportunities_for_portfolio(portfolio_case, portfolio, selected)
    ranked_map = {entry.opportunity_id: entry for entry in ranking.opportunities}
    selected_map = {opportunity.opportunity_id: opportunity for opportunity in selected}

    dimension_specs = [
        ("portfolio_fit", "Higher portfolio-fit score improves allocator suitability."),
        ("track_record", "Stronger manager track record improves conviction."),
        ("liquidity_impact", "Lower liquidity impact preserves pacing flexibility."),
        ("overlap_risk", "Lower overlap risk improves diversification value."),
        ("pacing_slot", "Higher pacing-slot score supports near-term commitment capacity."),
        ("esg_quality", "Higher ESG quality supports institutional sustainability priorities."),
    ]
    dimensions: list[OpportunityComparisonDimension] = []
    for category, explanation in dimension_specs:
        best_id: str | None = None
        best_value: float | None = None
        second_value: float | None = None
        for opportunity in selected:
            value = {
                "portfolio_fit": opportunity.portfolio_fit_score,
                "track_record": opportunity.track_record_score,
                "liquidity_impact": -opportunity.liquidity_impact_score,
                "overlap_risk": -opportunity.overlap_risk_score,
                "pacing_slot": opportunity.pacing_slot_score,
                "esg_quality": opportunity.esg_score,
            }[category]
            if best_value is None or value > best_value:
                second_value = best_value
                best_value = value
                best_id = opportunity.opportunity_id
            elif second_value is None or value > second_value:
                second_value = value
        difference = round((best_value - second_value), 4) if best_value is not None and second_value is not None else 0.0
        dimensions.append(
            OpportunityComparisonDimension(
                category=category,
                winner_opportunity_id=best_id,
                score_difference=difference,
                explanation=explanation,
            )
        )

    entries: list[OpportunityComparisonEntry] = []
    for opportunity_id in compared_opportunity_ids:
        ranked = ranked_map[opportunity_id]
        opportunity = selected_map[opportunity_id]
        strengths = [
            f"Portfolio fit score: {opportunity.portfolio_fit_score}",
            f"Track record score: {opportunity.track_record_score}",
            f"Pacing slot score: {opportunity.pacing_slot_score}",
        ]
        weaknesses = [
            f"Liquidity impact score: {opportunity.liquidity_impact_score}",
            f"Overlap risk score: {opportunity.overlap_risk_score}",
            f"Expected call profile: {opportunity.expected_call_profile}",
        ]
        entries.append(
            OpportunityComparisonEntry(
                opportunity_id=opportunity.opportunity_id,
                manager_name=opportunity.manager_name,
                fund_name=opportunity.fund_name,
                strategy=opportunity.strategy,
                vehicle_type=opportunity.vehicle_type,
                pipeline_stage=opportunity.pipeline_stage,
                composite_score=ranked.composite_score,
                recommended_action=ranked.recommended_action,
                strengths=strengths,
                weaknesses=weaknesses,
            )
        )

    preferred_opportunity_id = ranking.opportunities[0].opportunity_id if ranking.opportunities else None
    summary = (
        f"Preferred opportunity for {portfolio_case}: {ranked_map[preferred_opportunity_id].fund_name}."
        if preferred_opportunity_id is not None
        else "No preferred opportunity identified."
    )
    return OpportunityComparisonResult(
        portfolio_case=portfolio_case,
        compared_opportunity_ids=compared_opportunity_ids,
        preferred_opportunity_id=preferred_opportunity_id,
        entries=entries,
        dimensions=dimensions,
        summary=summary,
    )


def recommend_commitment(
    portfolio_case: str,
    portfolio: PortfolioSnapshot,
    opportunities: list[InvestmentOpportunity],
    opportunity_id: str,
) -> CommitmentRecommendationResult:
    ranking = rank_opportunities_for_portfolio(portfolio_case, portfolio, opportunities)
    ranked_map = {entry.opportunity_id: entry for entry in ranking.opportunities}
    opportunity_map = {opportunity.opportunity_id: opportunity for opportunity in opportunities}
    ranked = ranked_map[opportunity_id]
    opportunity = opportunity_map[opportunity_id]

    reasons: list[CommitmentRecommendationReason] = []
    conditions: list[str] = []

    if ranked.composite_score >= 60:
        recommendation = "advance"
        conviction = "high"
    elif ranked.composite_score >= 46:
        recommendation = "advance_with_conditions"
        conviction = "medium"
    elif ranked.composite_score >= 36:
        recommendation = "hold"
        conviction = "medium"
    else:
        recommendation = "decline"
        conviction = "low"

    if opportunity.portfolio_fit_score >= 7.5:
        reasons.append(
            CommitmentRecommendationReason(
                category="portfolio_fit",
                impact="positive",
                message="Portfolio fit is strong relative to current allocator objectives.",
            )
        )
    if opportunity.track_record_score >= 8.0:
        reasons.append(
            CommitmentRecommendationReason(
                category="track_record",
                impact="positive",
                message="Manager track record supports underwriting confidence.",
            )
        )
    if opportunity.overlap_risk_score >= 6.5:
        reasons.append(
            CommitmentRecommendationReason(
                category="overlap_risk",
                impact="negative",
                message="Existing portfolio overlap reduces incremental diversification value.",
            )
        )
        conditions.append("Re-test concentration and overlap versus current strategy bucket before approval.")
    if opportunity.liquidity_impact_score >= 6.8:
        reasons.append(
            CommitmentRecommendationReason(
                category="liquidity_impact",
                impact="negative",
                message="Liquidity impact is elevated relative to other current opportunities.",
            )
        )
        conditions.append("Confirm pacing capacity and reserve adequacy under downside distribution assumptions.")
    if opportunity.expected_call_profile == "fast":
        reasons.append(
            CommitmentRecommendationReason(
                category="call_profile",
                impact="negative",
                message="Fast call profile compresses pacing flexibility in the near term.",
            )
        )
        conditions.append("Stage commitment timing against the annual pacing budget.")
    if opportunity.vehicle_type == "re_up":
        reasons.append(
            CommitmentRecommendationReason(
                category="relationship",
                impact="positive",
                message="Existing GP relationship can shorten diligence time and improve execution certainty.",
            )
        )
    if opportunity.od_diligence_status != "completed":
        conditions.append("Complete operational due diligence before final committee approval.")
    if opportunity.legal_status == "not_started":
        conditions.append("Initiate legal review and side-letter workstream.")

    if not conditions and recommendation.startswith("advance"):
        conditions.append("No material gating items identified beyond standard IC process.")

    summary = (
        f"{recommendation.replace('_', ' ').title()} {opportunity.fund_name} for {portfolio_case} "
        f"with {conviction} conviction based on fit, pacing, and portfolio-overlap considerations."
    )
    return CommitmentRecommendationResult(
        portfolio_case=portfolio_case,
        opportunity_id=opportunity.opportunity_id,
        manager_name=opportunity.manager_name,
        fund_name=opportunity.fund_name,
        recommendation=recommendation,
        conviction=conviction,
        composite_score=ranked.composite_score,
        reasons=reasons,
        conditions=conditions,
        summary=summary,
    )
