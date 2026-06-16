from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from altintel.core.config import AppConfig
from altintel.core.models import DueDiligenceReport
from altintel.data.sample_data import load_json, load_named_proposed_commitment, list_commitment_cases
from altintel.due_diligence.service import run_due_diligence


@dataclass(slots=True)
class ExtractionEvalCase:
    commitment_case: str
    field_accuracy: float
    risk_recall: float
    fact_evidence_coverage: float
    risk_evidence_coverage: float
    matched_fields: int
    total_fields: int
    matched_risks: int
    total_risks: int


@dataclass(slots=True)
class ExtractionEvaluationResult:
    cases: list[ExtractionEvalCase]
    average_field_accuracy: float
    average_risk_recall: float
    average_fact_evidence_coverage: float
    average_risk_evidence_coverage: float


def _ground_truth_path(case_name: str) -> Path:
    return Path("data") / "synthetic" / f"ground_truth_{case_name}.json"


def _evaluate_case(report: DueDiligenceReport, ground_truth: dict[str, object], case_name: str) -> ExtractionEvalCase:
    extracted_fields = {
        "fund_name": report.facts.fund_name,
        "strategy": report.facts.strategy,
        "geography": report.facts.geography,
        "target_size_mn": report.facts.target_size_mn,
        "gp_commitment_pct": report.facts.gp_commitment_pct,
        "management_fee_pct": report.facts.management_fee_pct,
        "carry_pct": report.facts.carry_pct,
        "term_years": report.facts.term_years,
    }
    matched_fields = sum(1 for key, value in extracted_fields.items() if ground_truth.get(key) == value)
    expected_risks = set(ground_truth["risk_categories"])
    extracted_risks = {risk.category for risk in report.risks}
    matched_risks = len(expected_risks & extracted_risks)
    total_fields = len(extracted_fields)
    total_risks = len(expected_risks)
    fact_evidence_count = len(report.facts.evidence)
    fact_evidence_coverage = min(fact_evidence_count / 3, 1.0)
    risk_evidence_count = sum(1 for risk in report.risks if risk.evidence)
    risk_evidence_coverage = round(risk_evidence_count / len(report.risks), 4) if report.risks else 0.0
    return ExtractionEvalCase(
        commitment_case=case_name,
        field_accuracy=round(matched_fields / total_fields, 4),
        risk_recall=round(matched_risks / total_risks, 4) if total_risks else 0.0,
        fact_evidence_coverage=round(fact_evidence_coverage, 4),
        risk_evidence_coverage=risk_evidence_coverage,
        matched_fields=matched_fields,
        total_fields=total_fields,
        matched_risks=matched_risks,
        total_risks=total_risks,
    )


def run_extraction_evaluation(config: AppConfig) -> ExtractionEvaluationResult:
    cases: list[ExtractionEvalCase] = []
    for case_name in list_commitment_cases():
        memo = load_named_proposed_commitment(case_name=case_name)
        report = run_due_diligence(memo, config)
        ground_truth = load_json(_ground_truth_path(case_name))
        cases.append(_evaluate_case(report, ground_truth, case_name))

    average_field_accuracy = round(sum(case.field_accuracy for case in cases) / len(cases), 4) if cases else 0.0
    average_risk_recall = round(sum(case.risk_recall for case in cases) / len(cases), 4) if cases else 0.0
    average_fact_evidence_coverage = (
        round(sum(case.fact_evidence_coverage for case in cases) / len(cases), 4) if cases else 0.0
    )
    average_risk_evidence_coverage = (
        round(sum(case.risk_evidence_coverage for case in cases) / len(cases), 4) if cases else 0.0
    )
    return ExtractionEvaluationResult(
        cases=cases,
        average_field_accuracy=average_field_accuracy,
        average_risk_recall=average_risk_recall,
        average_fact_evidence_coverage=average_fact_evidence_coverage,
        average_risk_evidence_coverage=average_risk_evidence_coverage,
    )
