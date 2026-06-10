from __future__ import annotations

import re

from altintel.core.models import (
    DueDiligenceReport,
    EvidenceItem,
    ExtractedFundFacts,
    InvestmentMemoInput,
    RiskFinding,
)


def _extract_float(pattern: str, text: str) -> float:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Pattern not found: {pattern}")
    return float(match.group(1).replace(",", ""))


def _extract_int(pattern: str, text: str) -> int:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Pattern not found: {pattern}")
    return int(match.group(1))


def _extract_sentence_containing(text: str, phrase: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if phrase.lower() in line.lower():
            return line
    raise ValueError(f"Phrase not found in document: {phrase}")


def _risk_severity(text: str) -> str:
    lowered = text.lower()
    if "manageable" in lowered:
        return "medium"
    if "moderate" in lowered or "meaningful" in lowered:
        return "medium"
    return "high"


def extract_fund_facts(memo: InvestmentMemoInput) -> ExtractedFundFacts:
    text = memo.source_text
    evidence = [
        EvidenceItem(
            quote=_extract_sentence_containing(text, "target size is EUR"),
            section="Fund Overview",
        ),
        EvidenceItem(
            quote=_extract_sentence_containing(text, "The management fee is"),
            section="Terms and Economics",
        ),
        EvidenceItem(
            quote=_extract_sentence_containing(text, "Carried interest is"),
            section="Terms and Economics",
        ),
    ]

    return ExtractedFundFacts(
        fund_name=memo.fund_name,
        strategy=memo.strategy,
        geography=memo.geography,
        target_size_mn=_extract_float(r"target size is EUR ([0-9,]+) million", text),
        gp_commitment_pct=_extract_float(r"general partner commitment is ([0-9.]+)%", text),
        management_fee_pct=_extract_float(r"management fee is ([0-9.]+)%", text),
        carry_pct=_extract_float(r"Carried interest is ([0-9.]+)%", text),
        term_years=_extract_int(r"targeting a ([0-9]+)-year term", text),
        evidence=evidence,
    )


def extract_risk_findings(memo: InvestmentMemoInput) -> list[RiskFinding]:
    text = memo.source_text
    if memo.strategy == "timberland":
        risk_rows = [
            (
                "biological_weather",
                "Biological and weather risk is meaningful",
                "Biological growth and weather events can affect realizations",
                "Harvest timing and asset values are exposed to forestry-specific biological and climate conditions.",
                ["Review climate resilience assumptions and regional asset diversification."],
            ),
            (
                "exit_timing",
                "Exit-timing risk is moderate",
                "Timberland realizations may be delayed in softer buyer markets",
                "Long-duration assets can defer exits, which may slow liquidity conversion during weak demand periods.",
                ["Use longer hold assumptions in downside portfolio planning."],
            ),
            (
                "geographic_concentration",
                "Geographic concentration is manageable",
                "Northern Europe focus increases regional concentration",
                "Policy, weather, and export-market conditions may affect a concentrated regional strategy.",
                ["Monitor regional overlap with existing timberland and real-asset exposures."],
            ),
            (
                "operating_complexity",
                "Operating complexity is moderate",
                "Execution depends on forestry operations and contractor oversight",
                "Value creation relies on local operating execution rather than financial engineering alone.",
                ["Track certification compliance and contractor performance in monitoring packs."],
            ),
        ]
    else:
        risk_rows = [
            (
                "deployment_pacing",
                "Deployment risk remains relevant",
                "Deployment pacing may lag underwriting plan",
                "Slower capital deployment could defer value creation and push out distributions.",
                ["Use pacing downside case in portfolio liquidity planning."],
            ),
            (
                "financing_risk",
                "Financing risk is moderate",
                "Refinancing conditions may pressure asset-level outcomes",
                "Elevated base rates could weigh on refinancing flexibility and equity value realization.",
                ["Track leverage and refinancing maturity ladders in quarterly reviews."],
            ),
            (
                "sector_concentration",
                "Sector concentration is meaningful",
                "Renewables and digital infrastructure dominate target mix",
                "The portfolio is exposed to common demand and policy drivers across two major themes.",
                ["Assess overlap against existing infrastructure holdings before commitment approval."],
            ),
            (
                "key_person",
                "Key-person risk is manageable",
                "Decision-making remains concentrated in founding partners",
                "Team depth has improved, but investment judgment is still anchored in a small leadership group.",
                ["Require updates on succession planning and key-person provisions."],
            ),
        ]

    findings: list[RiskFinding] = []
    for category, phrase, title, rationale, mitigants in risk_rows:
        quote = _extract_sentence_containing(text, phrase)
        findings.append(
            RiskFinding(
                category=category,
                severity=_risk_severity(quote),
                title=title,
                rationale=rationale,
                mitigants=mitigants,
                evidence=[EvidenceItem(quote=quote, section="Risk Considerations")],
            )
        )
    return findings


def build_mock_due_diligence_report(memo: InvestmentMemoInput) -> DueDiligenceReport:
    facts = extract_fund_facts(memo)
    risks = extract_risk_findings(memo)
    validation_notes = [
        "Commitment amount in input file matches the document statement.",
        "Fee, carry, and term were extracted from explicit memo language.",
        "Risk findings are deterministic, asset-class aware, and evidence-linked for demo reproducibility.",
    ]
    return DueDiligenceReport(
        facts=facts,
        risks=risks,
        overall_risk_rating="medium",
        validation_notes=validation_notes,
    )
