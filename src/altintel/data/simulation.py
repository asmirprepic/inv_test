from __future__ import annotations

import json
import random
from datetime import date
from pathlib import Path

from altintel.core.models import HoldingObservation, PortfolioSnapshot


STRATEGY_PARAMETERS = {
    "infrastructure": {
        "growth_range": (0.01, 0.035),
        "margin_range": (0.34, 0.48),
        "leverage_range": (3.8, 5.8),
        "yield_range": (0.006, 0.018),
    },
    "real_estate": {
        "growth_range": (-0.005, 0.025),
        "margin_range": (0.28, 0.41),
        "leverage_range": (4.2, 6.3),
        "yield_range": (0.004, 0.014),
    },
    "timberland": {
        "growth_range": (0.0, 0.03),
        "margin_range": (0.22, 0.36),
        "leverage_range": (1.4, 3.1),
        "yield_range": (0.002, 0.01),
    },
    "private_equity_buyout": {
        "growth_range": (0.015, 0.05),
        "margin_range": (0.2, 0.34),
        "leverage_range": (4.8, 6.8),
        "yield_range": (0.0, 0.008),
    },
    "growth_equity": {
        "growth_range": (0.025, 0.08),
        "margin_range": (0.12, 0.26),
        "leverage_range": (1.0, 2.6),
        "yield_range": (0.0, 0.004),
    },
    "co_invest": {
        "growth_range": (0.02, 0.06),
        "margin_range": (0.16, 0.3),
        "leverage_range": (2.0, 4.8),
        "yield_range": (0.0, 0.006),
    },
}


def _quarter_end_dates(as_of: date, quarters: int) -> list[date]:
    dates: list[date] = []
    year = as_of.year
    month = ((as_of.month - 1) // 3 + 1) * 3
    current = date(year, month, min(as_of.day, 28))
    for offset in range(quarters - 1, -1, -1):
        q_month = current.month - offset * 3
        q_year = current.year
        while q_month <= 0:
            q_month += 12
            q_year -= 1
        dates.append(date(q_year, q_month, 28))
    return dates


def generate_portfolio_monitoring_data(
    portfolio: PortfolioSnapshot,
    quarters: int = 12,
    seed: int = 7,
) -> list[HoldingObservation]:
    rng = random.Random(seed)
    dates = _quarter_end_dates(portfolio.as_of, quarters)
    observations: list[HoldingObservation] = []

    for holding_index, holding in enumerate(portfolio.holdings):
        params = STRATEGY_PARAMETERS.get(holding.strategy, STRATEGY_PARAMETERS["infrastructure"])
        nav = max(holding.nav_mn * rng.uniform(0.74, 0.92), 1.0)
        unfunded_remaining = holding.unfunded_mn

        for quarter_index, as_of in enumerate(dates):
            growth = rng.uniform(*params["growth_range"])
            margin = rng.uniform(*params["margin_range"])
            leverage = rng.uniform(*params["leverage_range"])
            yield_rate = rng.uniform(*params["yield_range"])

            contribution = 0.0
            if unfunded_remaining > 0:
                contribution_share = min(unfunded_remaining, holding.unfunded_mn * rng.uniform(0.04, 0.14))
                contribution = round(contribution_share, 4)
                unfunded_remaining = round(max(unfunded_remaining - contribution_share, 0.0), 4)

            distribution = round(nav * yield_rate, 4)
            valuation_change = growth - rng.uniform(0.004, 0.018)
            nav = max(nav * (1 + valuation_change) + contribution - distribution, 0.5)

            # Inject a small number of deterministic stress events so monitoring has real signals.
            if quarter_index == len(dates) - 1 and (holding_index + seed) % 4 == 0:
                leverage += 1.15
                valuation_change -= 0.06
                nav = max(nav * 0.92, 0.5)
            if quarter_index == len(dates) - 2 and (holding_index + seed) % 5 == 0:
                distribution *= 0.35
                growth -= 0.03

            observations.append(
                HoldingObservation(
                    as_of=as_of,
                    holding_name=holding.name,
                    strategy=holding.strategy,
                    nav_mn=round(nav, 4),
                    contribution_mn=round(contribution, 4),
                    distribution_mn=round(distribution, 4),
                    revenue_growth_pct=round(growth * 100, 4),
                    ebitda_margin_pct=round(margin * 100, 4),
                    leverage_ratio=round(leverage, 4),
                    valuation_change_pct=round(valuation_change * 100, 4),
                )
            )
    return observations


def export_monitoring_data(observations: list[HoldingObservation], path: str | Path) -> None:
    export_path = Path(path)
    export_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "as_of": observation.as_of.isoformat(),
            "holding_name": observation.holding_name,
            "strategy": observation.strategy,
            "nav_mn": observation.nav_mn,
            "contribution_mn": observation.contribution_mn,
            "distribution_mn": observation.distribution_mn,
            "revenue_growth_pct": observation.revenue_growth_pct,
            "ebitda_margin_pct": observation.ebitda_margin_pct,
            "leverage_ratio": observation.leverage_ratio,
            "valuation_change_pct": observation.valuation_change_pct,
        }
        for observation in observations
    ]
    export_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
