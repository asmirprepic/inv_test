from __future__ import annotations

from altintel.core.config import AppConfig
from altintel.core.models import DueDiligenceReport, InvestmentMemoInput
from altintel.llm.clients import build_due_diligence_client


def run_due_diligence(memo: InvestmentMemoInput, config: AppConfig) -> DueDiligenceReport:
    provider = config.model["llm"]["provider"]
    client = build_due_diligence_client(provider)
    return client.extract_due_diligence(memo)
