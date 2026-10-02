from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ResearchTask:
    """
    One atomic research task generated for a person.

    A task describes what PERSONA-X should investigate.
    It does not itself claim that any fact is true.
    """

    task_id: str
    query_text: str

    query_type: str
    profession_context: Optional[str] = None
    topic: Optional[str] = None

    priority: int = 5
    rationale: Optional[str] = None

    source_quality: str = "mixed"
    temporal_scope: Optional[str] = None

    status: str = "planned"


@dataclass
class ResearchPlan:
    """
    Complete research plan for one person.

    The plan is a structured research map, not the research result.
    """

    person_name: str

    professions: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)

    tasks: List[ResearchTask] = field(default_factory=list)

    research_scope: str = "comprehensive"

    political_research_justified: bool = False
    political_research_reason: Optional[str] = None

    planner_version: str = "1.0"

    def add_task(self, task: ResearchTask) -> None:
        self.tasks.append(task)

    @property
    def task_count(self) -> int:
        return len(self.tasks)