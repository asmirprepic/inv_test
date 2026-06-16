from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod

from altintel.core.models import DueDiligenceReport, EvidenceItem, ExtractedFundFacts, InvestmentMemoInput, RiskFinding
from altintel.due_diligence.extractors import _extract_sentence_containing, _risk_severity
from altintel.llm.prompts import build_due_diligence_extraction_prompt


class BaseDueDiligenceClient(ABC):
    @abstractmethod
    def extract_due_diligence(self, memo: InvestmentMemoInput) -> DueDiligenceReport:
        raise NotImplementedError


class MockDueDiligenceClient(BaseDueDiligenceClient):
    def extract_due_diligence(self, memo: InvestmentMemoInput) -> DueDiligenceReport:
        from altintel.due_diligence.extractors import build_mock_due_diligence_report

        return build_mock_due_diligence_report(memo)


class OpenAICompatibleDueDiligenceClient(BaseDueDiligenceClient):
    def __init__(self, model: str, temperature: float = 0.0, max_tokens: int = 1200) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = os.environ.get("ALTINTEL_OPENAI_API_KEY", "")
        self.base_url = os.environ.get("ALTINTEL_OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    def extract_due_diligence(self, memo: InvestmentMemoInput) -> DueDiligenceReport:
        if not self.api_key:
            raise ValueError("ALTINTEL_OPENAI_API_KEY is required for openai_compatible provider")

        prompt = build_due_diligence_extraction_prompt(memo)
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
        }
        request = urllib.request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ValueError(f"LLM request failed: {exc.code} {detail}") from exc

        content = response_payload["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        _validate_llm_payload(parsed, memo)
        return _report_from_llm_payload(parsed, memo)


def _allowed_risk_categories(strategy: str) -> set[str]:
    if strategy == "timberland":
        return {"biological_weather", "exit_timing", "geographic_concentration", "operating_complexity"}
    return {"deployment_pacing", "financing_risk", "sector_concentration", "key_person"}


def _validate_llm_payload(payload: dict[str, object], memo: InvestmentMemoInput) -> None:
    required_fact_fields = {
        "fund_name",
        "strategy",
        "geography",
        "target_size_mn",
        "gp_commitment_pct",
        "management_fee_pct",
        "carry_pct",
        "term_years",
    }
    facts_payload = payload.get("facts")
    if not isinstance(facts_payload, dict):
        raise ValueError("LLM payload must contain a 'facts' object")

    missing = required_fact_fields - set(facts_payload)
    if missing:
        raise ValueError(f"LLM payload missing required fact fields: {sorted(missing)}")

    for field_name in required_fact_fields:
        entry = facts_payload[field_name]
        if not isinstance(entry, dict):
            raise ValueError(f"Fact entry must be an object: {field_name}")
        if "value" not in entry or "confidence" not in entry:
            raise ValueError(f"Fact entry missing value/confidence: {field_name}")

    risks = payload.get("risks", [])
    if not isinstance(risks, list):
        raise ValueError("LLM payload 'risks' must be a list")

    allowed_categories = _allowed_risk_categories(memo.strategy)
    for risk in risks:
        if not isinstance(risk, dict):
            raise ValueError("Each risk entry must be an object")
        category = str(risk.get("category", ""))
        if category not in allowed_categories:
            raise ValueError(f"Unsupported risk category for strategy {memo.strategy}: {category}")
        if not str(risk.get("evidence_quote", "")).strip():
            raise ValueError(f"Risk entry missing evidence_quote: {category}")
        if str(risk.get("severity", "")) not in {"low", "medium", "high"}:
            raise ValueError(f"Risk entry has invalid severity: {category}")


def _report_from_llm_payload(payload: dict[str, object], memo: InvestmentMemoInput) -> DueDiligenceReport:
    facts_payload = payload.get("facts", {})
    if not isinstance(facts_payload, dict):
        raise ValueError("LLM payload missing 'facts' object")

    def _fact_entry(name: str) -> dict[str, object]:
        entry = facts_payload.get(name, {})
        if not isinstance(entry, dict):
            raise ValueError(f"LLM fact entry must be an object: {name}")
        return entry

    def _fact_value(name: str, default: object = None) -> object:
        return _fact_entry(name).get("value", default)

    def _fact_evidence(name: str, fallback_phrase: str, fallback_section: str) -> EvidenceItem:
        entry = _fact_entry(name)
        quote = str(entry.get("evidence_quote", "")).strip()
        section = str(entry.get("evidence_section", "")).strip()
        if quote and section:
            return EvidenceItem(quote=quote, section=section)
        return EvidenceItem(
            quote=_extract_sentence_containing(memo.source_text, fallback_phrase),
            section=fallback_section,
        )

    facts = ExtractedFundFacts(
        fund_name=str(_fact_value("fund_name", memo.fund_name)),
        strategy=str(_fact_value("strategy", memo.strategy)),
        geography=str(_fact_value("geography", memo.geography)),
        target_size_mn=float(_fact_value("target_size_mn", 0.0) or 0.0),
        gp_commitment_pct=float(_fact_value("gp_commitment_pct", 0.0) or 0.0),
        management_fee_pct=float(_fact_value("management_fee_pct", 0.0) or 0.0),
        carry_pct=float(_fact_value("carry_pct", 0.0) or 0.0),
        term_years=int(_fact_value("term_years", 0) or 0),
        evidence=[
            _fact_evidence("target_size_mn", "target size is EUR", "Fund Overview"),
            _fact_evidence("management_fee_pct", "The management fee is", "Terms and Economics"),
            _fact_evidence("carry_pct", "Carried interest is", "Terms and Economics"),
        ],
    )
    risks: list[RiskFinding] = []
    for item in payload.get("risks", []):
        risk = item if isinstance(item, dict) else {}
        rationale = str(risk.get("rationale", ""))
        title = str(risk.get("title", ""))
        category = str(risk.get("category", "unknown"))
        risks.append(
            RiskFinding(
                category=category,
                severity=str(risk.get("severity", _risk_severity(rationale or title))),
                title=title or category.replace("_", " ").title(),
                rationale=rationale,
                evidence=[
                    EvidenceItem(
                        quote=str(risk.get("evidence_quote", "")).strip(),
                        section=str(risk.get("evidence_section", "Risk Considerations")).strip() or "Risk Considerations",
                    )
                ]
                if str(risk.get("evidence_quote", "")).strip()
                else [],
            )
        )
    return DueDiligenceReport(
        facts=facts,
        risks=risks,
        overall_risk_rating=str(payload.get("overall_risk_rating", "medium")),
        validation_notes=[str(note) for note in payload.get("validation_notes", [])],
    )


def build_due_diligence_client(
    provider: str,
    model: str = "deterministic-demo",
    temperature: float = 0.0,
    max_tokens: int = 1200,
) -> BaseDueDiligenceClient:
    if provider == "mock":
        return MockDueDiligenceClient()
    if provider == "openai_compatible":
        return OpenAICompatibleDueDiligenceClient(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    raise ValueError(f"Unsupported due diligence provider: {provider}")
