from __future__ import annotations

from crewai import Agent
from crewai.tools import BaseTool

from .config import load_settings


class InsuranceKnowledgeSearchTool(BaseTool):
    name: str = "insurance_knowledge_search"
    description: str = (
        "Returns pre-collected insurance evidence from RAG/web context. "
        "Use this to ground your answer."
    )
    evidence_seed: str = ""

    def _run(self, query: str) -> str:
        del query
        return self.evidence_seed or "No evidence provided."


def build_llm() -> str:
    
    settings = load_settings()
    return f"groq/{settings.groq_model}"


def build_agents(evidence_seed: str = "") -> tuple[Agent, Agent]:
    llm = build_llm()
    tool = InsuranceKnowledgeSearchTool(evidence_seed=evidence_seed)

    researcher_agent = Agent(
        role="Insurance Researcher",
        goal="Extract accurate policy facts, exclusions, and risks from available evidence.",
        backstory=(
            "A senior insurance analyst who validates details and avoids unsupported claims."
        ),
        tools=[tool],
        llm=llm,
        verbose=True,
    )

    writer_agent = Agent(
        role="Insurance Writer",
        goal="Turn research into user-ready structured guidance for insurance decisions.",
        backstory=(
            "A policy communication specialist who explains risk, coverage, cost impact, and prevention."
        ),
        tools=[tool],
        llm=llm,
        verbose=True,
    )

    return researcher_agent, writer_agent
