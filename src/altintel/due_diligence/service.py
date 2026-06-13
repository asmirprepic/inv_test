from __future__ import annotations

from altintel.core.config import AppConfig
from altintel.core.models import DueDiligenceReport, InvestmentMemoInput
from altintel.llm.clients import build_due_diligence_client


def run_due_diligence(memo: InvestmentMemoInput, config: AppConfig) -> DueDiligenceReport:
    llm_config = config.model["llm"]
    client = build_due_diligence_client(
        provider=llm_config["provider"],
        model=llm_config["model"],
        temperature=float(llm_config["temperature"]),
        max_tokens=int(llm_config["max_tokens"]),
    )
    return client.extract_due_diligence(memo)
