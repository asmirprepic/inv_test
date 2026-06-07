from __future__ import annotations

from abc import ABC, abstractmethod

from altintel.core.models import DueDiligenceReport, InvestmentMemoInput


class BaseDueDiligenceClient(ABC):
    @abstractmethod
    def extract_due_diligence(self, memo: InvestmentMemoInput) -> DueDiligenceReport:
        raise NotImplementedError


class MockDueDiligenceClient(BaseDueDiligenceClient):
    def extract_due_diligence(self, memo: InvestmentMemoInput) -> DueDiligenceReport:
        from altintel.due_diligence.extractors import build_mock_due_diligence_report

        return build_mock_due_diligence_report(memo)


def build_due_diligence_client(provider: str) -> BaseDueDiligenceClient:
    if provider == "mock":
        return MockDueDiligenceClient()
    raise ValueError(f"Unsupported due diligence provider: {provider}")
