from __future__ import annotations

import re
from dataclasses import dataclass

from altintel.core.models import InvestmentMemoInput


@dataclass(slots=True)
class RetrievedSection:
    section: str
    score: int
    content: str


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z_]+", text.lower())


def _split_memo_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_heading = "Document Overview"
    current_lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            if current_lines:
                sections.append((current_heading, current_lines))
            current_heading = line.removeprefix("## ").strip()
            current_lines = []
            continue
        if line.strip():
            current_lines.append(line.strip())

    if current_lines:
        sections.append((current_heading, current_lines))

    return [(heading, " ".join(lines)) for heading, lines in sections]


def retrieve_relevant_sections(
    memo: InvestmentMemoInput,
    query: str,
    top_k: int = 3,
) -> list[RetrievedSection]:
    query_tokens = set(_tokenize(query))
    results: list[RetrievedSection] = []
    for section, content in _split_memo_sections(memo.source_text):
        content_tokens = _tokenize(content)
        score = sum(1 for token in content_tokens if token in query_tokens)
        if score > 0:
            results.append(RetrievedSection(section=section, score=score, content=content))
    ordered = sorted(results, key=lambda item: (-item.score, item.section))
    return ordered[:top_k]


def build_retrieval_packet(memo: InvestmentMemoInput) -> str:
    fact_queries = [
        "fund name strategy geography target size",
        "general partner commitment management fee carried interest",
        "term hard cap investment period economics",
    ]
    risk_queries = [
        "risk considerations financing deployment concentration key person",
        "biological weather exit timing operating complexity concentration",
    ]

    selected: dict[str, RetrievedSection] = {}
    for query in fact_queries + risk_queries:
        for result in retrieve_relevant_sections(memo, query):
            selected[result.section] = result

    ordered = sorted(selected.values(), key=lambda item: (-item.score, item.section))
    packet_lines = ["Retrieved memo context:"]
    for result in ordered:
        packet_lines.append(f"[Section: {result.section} | relevance_score: {result.score}]")
        packet_lines.append(result.content)
    return "\n".join(packet_lines)
