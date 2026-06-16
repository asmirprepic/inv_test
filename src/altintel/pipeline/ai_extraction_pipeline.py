from __future__ import annotations

from dataclasses import dataclass

from altintel.core import AppConfig, DueDiligenceReport, InvestmentMemoInput
from altintel.data.sample_data import load_named_proposed_commitment
from altintel.due_diligence.service import run_due_diligence
from altintel.llm.retrieval import RetrievedSection, retrieve_relevant_sections


@dataclass(slots=True)
class AIExtractionPipelineResult:
    commitment_case: str
    memo: InvestmentMemoInput
    retrieved_sections: list[RetrievedSection]
    due_diligence_report: DueDiligenceReport
    fact_evidence_coverage: float
    risk_evidence_coverage: float
    validation_passed: bool


def _build_retrieval_plan(memo: InvestmentMemoInput) -> list[RetrievedSection]:
    queries = [
        "fund strategy geography target size general partner commitment",
        "management fee carried interest term economics",
        "risk considerations concentration financing key person deployment",
        "biological weather exit timing operating complexity concentration",
    ]
    selected: dict[tuple[str, str], RetrievedSection] = {}
    for query in queries:
        for result in retrieve_relevant_sections(memo, query, top_k=2):
            selected[(result.section, result.content)] = result
    return sorted(selected.values(), key=lambda item: (-item.score, item.section))


def _fact_evidence_coverage(report: DueDiligenceReport) -> float:
    expected_evidence_items = 3
    return round(min(len(report.facts.evidence) / expected_evidence_items, 1.0), 4)


def _risk_evidence_coverage(report: DueDiligenceReport) -> float:
    if not report.risks:
        return 0.0
    covered = sum(1 for risk in report.risks if risk.evidence)
    return round(covered / len(report.risks), 4)


def run_ai_extraction_pipeline(
    config: AppConfig,
    commitment_case: str = "infrastructure",
) -> AIExtractionPipelineResult:
    memo = load_named_proposed_commitment(case_name=commitment_case)
    retrieved_sections = _build_retrieval_plan(memo)
    report = run_due_diligence(memo, config)
    fact_coverage = _fact_evidence_coverage(report)
    risk_coverage = _risk_evidence_coverage(report)
    validation_passed = fact_coverage >= 1.0 and risk_coverage >= 1.0 and bool(report.risks)

    return AIExtractionPipelineResult(
        commitment_case=commitment_case,
        memo=memo,
        retrieved_sections=retrieved_sections,
        due_diligence_report=report,
        fact_evidence_coverage=fact_coverage,
        risk_evidence_coverage=risk_coverage,
        validation_passed=validation_passed,
    )
