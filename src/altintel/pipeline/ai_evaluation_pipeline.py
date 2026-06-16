from __future__ import annotations

from dataclasses import dataclass

from altintel.core import AppConfig
from altintel.due_diligence.evaluation import ExtractionEvaluationResult, run_extraction_evaluation


@dataclass(slots=True)
class AIEvaluationThresholds:
    min_field_accuracy: float = 0.95
    min_risk_recall: float = 0.95
    min_fact_evidence_coverage: float = 0.95
    min_risk_evidence_coverage: float = 0.95


@dataclass(slots=True)
class AIEvaluationPipelineResult:
    provider: str
    model: str
    thresholds: AIEvaluationThresholds
    evaluation: ExtractionEvaluationResult
    passed: bool
    failed_checks: list[str]


def run_ai_evaluation_pipeline(
    config: AppConfig,
    thresholds: AIEvaluationThresholds | None = None,
) -> AIEvaluationPipelineResult:
    active_thresholds = thresholds or AIEvaluationThresholds()
    evaluation = run_extraction_evaluation(config)
    failed_checks: list[str] = []

    if evaluation.average_field_accuracy < active_thresholds.min_field_accuracy:
        failed_checks.append("average_field_accuracy")
    if evaluation.average_risk_recall < active_thresholds.min_risk_recall:
        failed_checks.append("average_risk_recall")
    if evaluation.average_fact_evidence_coverage < active_thresholds.min_fact_evidence_coverage:
        failed_checks.append("average_fact_evidence_coverage")
    if evaluation.average_risk_evidence_coverage < active_thresholds.min_risk_evidence_coverage:
        failed_checks.append("average_risk_evidence_coverage")

    llm_config = config.model["llm"]
    return AIEvaluationPipelineResult(
        provider=str(llm_config["provider"]),
        model=str(llm_config["model"]),
        thresholds=active_thresholds,
        evaluation=evaluation,
        passed=not failed_checks,
        failed_checks=failed_checks,
    )
