from typing import Iterable, List, Optional
import re

from engine.research.planner_schemas import ResearchPlan, ResearchTask
from engine.research.taxonomy import (
    POLITICAL_RESEARCH_AREAS,
    PROFESSION_RESEARCH_AREAS,
    UNIVERSAL_RESEARCH_AREAS,
)


class UniversalResearchPlanner:
    """
    Deterministically converts a person's identity and professions
    into a structured research plan.

    This planner creates research tasks only. It does not claim
    that any underlying fact is true.
    """

    PROFESSION_ALIASES = {
        "sportsman": "athlete",
        "sportsperson": "athlete",
        "cricketer": "athlete",
        "footballer": "athlete",
        "soccer player": "athlete",
        "actor": "actor",
        "actress": "actor",
        "film actor": "actor",
        "scientist": "scientist",
        "researcher": "scientist",
        "entrepreneur": "entrepreneur",
        "businessperson": "entrepreneur",
        "businessman": "entrepreneur",
        "businesswoman": "entrepreneur",
        "politician": "politician",
        "political leader": "politician",
        "journalist": "journalist",
        "reporter": "journalist",
        "author": "author",
        "writer": "author",
        "academic": "academic",
        "professor": "academic",
        "artist": "artist",
    }

    def normalize_text(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = " ".join(value.split()).strip()
        return normalized or None

    def normalize_profession(self, profession: str) -> Optional[str]:
        normalized = self.normalize_text(profession)

        if not normalized:
            return None

        key = normalized.lower()

        if key in self.PROFESSION_ALIASES:
            return self.PROFESSION_ALIASES[key]

        return key

    def normalize_professions(
        self,
        professions: Iterable[str],
    ) -> List[str]:
        normalized: List[str] = []

        for profession in professions:
            value = self.normalize_profession(profession)

            if value and value not in normalized:
                normalized.append(value)

        return normalized

    def slugify(self, value: str) -> str:
        value = value.lower().strip()
        value = re.sub(r"[^a-z0-9]+", "_", value)
        return value.strip("_")

    def build_query(
        self,
        person_name: str,
        area_name: str,
        description: str,
        aliases: Optional[List[str]] = None,
    ) -> str:
        identity = person_name

        if aliases:
            alias_text = " ".join(
                alias for alias in aliases
                if alias and alias != person_name
            )

            if alias_text:
                identity = f"{person_name} {alias_text}"

        return (
            f'"{identity}" {area_name.replace("_", " ")} '
            f"{description}"
        )

    def create_task(
        self,
        person_name: str,
        area_name: str,
        definition: dict,
        aliases: Optional[List[str]] = None,
        profession_context: Optional[str] = None,
        temporal_scope: Optional[str] = None,
    ) -> ResearchTask:
        query_type = str(definition["query_type"])

        profession_part = (
            profession_context
            if profession_context
            else "universal"
        )

        task_id = "_".join(
            [
                self.slugify(person_name),
                self.slugify(profession_part),
                self.slugify(query_type),
                self.slugify(area_name),
            ]
        )

        return ResearchTask(
            task_id=task_id,
            query_text=self.build_query(
                person_name=person_name,
                area_name=area_name,
                description=str(definition["description"]),
                aliases=aliases,
            ),
            query_type=query_type,
            profession_context=profession_context,
            topic=area_name,
            priority=int(definition["priority"]),
            rationale=str(definition["description"]),
            source_quality=str(definition["source_quality"]),
            temporal_scope=temporal_scope,
            status="planned",
        )

    def add_universal_tasks(
        self,
        plan: ResearchPlan,
        temporal_scope: Optional[str] = None,
    ) -> None:
        for area_name, definition in UNIVERSAL_RESEARCH_AREAS.items():
            task = self.create_task(
                person_name=plan.person_name,
                area_name=area_name,
                definition=definition,
                aliases=plan.aliases,
                temporal_scope=temporal_scope,
            )

            plan.add_task(task)

    def add_profession_tasks(
        self,
        plan: ResearchPlan,
        profession: str,
        temporal_scope: Optional[str] = None,
    ) -> None:
        areas = PROFESSION_RESEARCH_AREAS.get(profession, {})

        for area_name, definition in areas.items():
            task = self.create_task(
                person_name=plan.person_name,
                area_name=area_name,
                definition=definition,
                aliases=plan.aliases,
                profession_context=profession,
                temporal_scope=temporal_scope,
            )

            plan.add_task(task)

    def add_political_tasks(
        self,
        plan: ResearchPlan,
        temporal_scope: Optional[str] = None,
    ) -> None:
        for area_name, definition in POLITICAL_RESEARCH_AREAS.items():
            task = self.create_task(
                person_name=plan.person_name,
                area_name=area_name,
                definition=definition,
                aliases=plan.aliases,
                profession_context="political_research",
                temporal_scope=temporal_scope,
            )

            plan.add_task(task)

    def deduplicate_tasks(
        self,
        tasks: List[ResearchTask],
    ) -> List[ResearchTask]:
        seen = set()
        deduplicated = []

        for task in tasks:
            key = (
                task.query_type,
                task.profession_context,
                task.topic,
            )

            if key in seen:
                continue

            seen.add(key)
            deduplicated.append(task)

        return deduplicated

    def sort_tasks(
        self,
        tasks: List[ResearchTask],
    ) -> List[ResearchTask]:
        return sorted(
            tasks,
            key=lambda task: (
                -task.priority,
                task.task_id,
            ),
        )

    def build_plan(
        self,
        person_name: str,
        professions: Optional[Iterable[str]] = None,
        aliases: Optional[Iterable[str]] = None,
        research_scope: str = "comprehensive",
        temporal_scope: Optional[str] = "full_career",
        political_research_justified: bool = False,
        political_research_reason: Optional[str] = None,
    ) -> ResearchPlan:
        normalized_name = self.normalize_text(person_name)

        if not normalized_name:
            raise ValueError("Person name cannot be empty.")

        normalized_professions = self.normalize_professions(
            professions or []
        )

        normalized_aliases = []

        for alias in aliases or []:
            value = self.normalize_text(alias)

            if value and value not in normalized_aliases:
                normalized_aliases.append(value)

        plan = ResearchPlan(
            person_name=normalized_name,
            professions=normalized_professions,
            aliases=normalized_aliases,
            research_scope=self.normalize_text(research_scope)
            or "comprehensive",
            political_research_justified=political_research_justified,
            political_research_reason=self.normalize_text(
                political_research_reason
            ),
        )

        self.add_universal_tasks(
            plan=plan,
            temporal_scope=temporal_scope,
        )

        for profession in normalized_professions:
            self.add_profession_tasks(
                plan=plan,
                profession=profession,
                temporal_scope=temporal_scope,
            )

        if political_research_justified:
            self.add_political_tasks(
                plan=plan,
                temporal_scope=temporal_scope,
            )

        plan.tasks = self.deduplicate_tasks(plan.tasks)
        plan.tasks = self.sort_tasks(plan.tasks)

        return plan