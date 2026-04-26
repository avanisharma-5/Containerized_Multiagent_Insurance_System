from __future__ import annotations

from crewai import Task


def build_tasks(researcher_agent, writer_agent) -> tuple[Task, Task]:
    research_task = Task(
        description=(
            "Analyze insurance query: {question}\n"
            "Chat history (if provided): {chat_history}\n"
            "Use the evidence tool to collect relevant grounded facts."
        ),
        expected_output=(
            "Bullet points covering risks, coverage items, exclusions, and key conditions."
        ),
        agent=researcher_agent,
    )

    writer_task = Task(
        description=(
            "Write final response for: {question}\n"
            "Use only evidence from research context and tool.\n"
            "Output sections: Risks, Coverage, Cost Impact, Prevention, Limitations."
        ),
        expected_output="A concise, structured insurance answer with practical next steps.",
        agent=writer_agent,
        context=[research_task],
    )

    return research_task, writer_task
