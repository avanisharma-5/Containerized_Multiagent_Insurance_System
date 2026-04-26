from __future__ import annotations

from crewai import Crew, Process

from .agents import build_agents
from .tasks import build_tasks


def build_insurance_crew(evidence_seed: str = "") -> Crew:
    researcher_agent, writer_agent = build_agents(evidence_seed=evidence_seed)
    research_task, writer_task = build_tasks(researcher_agent, writer_agent)
    return Crew(
        agents=[researcher_agent, writer_agent],
        tasks=[research_task, writer_task],
        process=Process.sequential,
        verbose=True,
    )
