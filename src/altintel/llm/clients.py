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
        return _report_from_llm_payload(parsed, memo)


def _report_from_llm_payload(payload: dict[str, object], memo: InvestmentMemoInput) -> DueDiligenceReport:
    facts = ExtractedFundFacts(
        fund_name=str(payload["fund_name"]),
        strategy=str(payload["strategy"]),
        geography=str(payload["geography"]),
        target_size_mn=float(payload["target_size_mn"]),
        gp_commitment_pct=float(payload["gp_commitment_pct"]),
        management_fee_pct=float(payload["management_fee_pct"]),
        carry_pct=float(payload["carry_pct"]),
        term_years=int(payload["term_years"]),
        evidence=[
            EvidenceItem(
                quote=_extract_sentence_containing(memo.source_text, "target size is EUR"),
                section="Fund Overview",
            ),
            EvidenceItem(
                quote=_extract_sentence_containing(memo.source_text, "The management fee is"),
                section="Terms and Economics",
            ),
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
                evidence=[],
            )
        )
    return DueDiligenceReport(
        facts=facts,
        risks=risks,
        overall_risk_rating="medium",
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
