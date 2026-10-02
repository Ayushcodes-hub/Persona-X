from typing import Dict, List, Optional, Tuple

from engine.identity.context import IdentityContext
from engine.research.planner_schemas import ResearchTask
from engine.research.query_schemas import QueryBundle, QueryVariant


class ResearchQueryGenerator:
    """
    Converts one research task into targeted search-query variants.

    This component generates discovery queries only. It does not assert
    that any returned search result is accurate or relevant.

    Query generation is intentionally separated from source verification:
    generated queries express research intent, while later source-verification
    components determine the quality and authority of discovered sources.

    Verified identity context may optionally be supplied to improve
    disambiguation. No identity facts are invented by this component.
    """

    PROFESSION_QUERY_FAMILIES: Dict[
        str, List[Tuple[str, str, str, Optional[str]]]
    ] = {
        "athlete": [
            (
                "teams",
                "teams clubs leagues competitions",
                "professional",
                "sports_governing_body",
            ),
            (
                "records",
                "records statistics achievements",
                "professional",
                "sports_statistics",
            ),
            (
                "awards",
                "awards honors recognition",
                "professional",
                "sports_awards",
            ),
            (
                "interviews",
                "interview career views",
                "interview",
                "major_media",
            ),
            (
                "endorsements",
                "endorsements brands partnerships",
                "business",
                "company_or_brand",
            ),
            (
                "philanthropy",
                "charity philanthropy foundation",
                "public_activity",
                "foundation_or_ngo",
            ),
        ],
        "actor": [
            (
                "filmography",
                "films television roles filmography",
                "professional",
                "film_database_or_studio",
            ),
            (
                "awards",
                "awards nominations honors",
                "professional",
                "award_body",
            ),
            (
                "interviews",
                "interview acting career views",
                "interview",
                "major_media",
            ),
            (
                "production",
                "production company projects",
                "business",
                "company",
            ),
            (
                "endorsements",
                "endorsements brands partnerships",
                "business",
                "company_or_brand",
            ),
            (
                "philanthropy",
                "charity philanthropy foundation",
                "public_activity",
                "foundation_or_ngo",
            ),
        ],
        "scientist": [
            (
                "research",
                "research publications discoveries",
                "academic",
                "academic_or_research_institution",
            ),
            (
                "institutions",
                "university laboratory institution",
                "academic",
                "academic_institution",
            ),
            (
                "awards",
                "scientific awards honors",
                "academic",
                "award_body",
            ),
            (
                "patents",
                "patents inventions",
                "academic",
                "patent_database",
            ),
            (
                "lectures",
                "lectures talks interviews",
                "interview",
                "academic_or_major_media",
            ),
            (
                "science_policy",
                "science policy public statements",
                "public_policy",
                "government_or_academic",
            ),
        ],
        "entrepreneur": [
            (
                "companies",
                "companies founder executive",
                "business",
                "company",
            ),
            (
                "funding",
                "funding investment financing",
                "business",
                "financial_or_company",
            ),
            (
                "products",
                "products companies launches",
                "business",
                "company",
            ),
            (
                "acquisitions",
                "acquisitions mergers",
                "business",
                "regulatory_or_company",
            ),
            (
                "interviews",
                "interview business philosophy",
                "interview",
                "major_media",
            ),
            (
                "public_policy",
                "public policy statements",
                "public_policy",
                "government_or_major_media",
            ),
        ],
        "politician": [
            (
                "elections",
                "elections campaigns results",
                "political",
                "election_authority",
            ),
            (
                "office",
                "office government role",
                "official",
                "government",
            ),
            (
                "legislation",
                "legislation bills votes",
                "political",
                "legislature",
            ),
            (
                "speeches",
                "speeches public statements",
                "political",
                "official_or_major_media",
            ),
            (
                "policy",
                "policy positions government actions",
                "public_policy",
                "government_or_legislature",
            ),
            (
                "initiatives",
                "government initiatives programs",
                "public_activity",
                "government",
            ),
        ],
        "journalist": [
            (
                "publications",
                "articles reporting publications",
                "professional",
                "publisher",
            ),
            (
                "broadcasts",
                "television radio broadcasts",
                "professional",
                "broadcaster",
            ),
            (
                "interviews",
                "interviews journalism career",
                "interview",
                "major_media",
            ),
            (
                "awards",
                "journalism awards honors",
                "professional",
                "award_body",
            ),
            (
                "investigations",
                "investigations investigative reporting",
                "professional",
                "publisher_or_institution",
            ),
            (
                "media_activity",
                "media organizations public activity",
                "public_activity",
                "media_organization",
            ),
        ],
        "author": [
            (
                "books",
                "books publications bibliography",
                "professional",
                "publisher_or_library",
            ),
            (
                "awards",
                "literary awards honors",
                "professional",
                "award_body",
            ),
            (
                "interviews",
                "interview writing views",
                "interview",
                "major_media",
            ),
            (
                "lectures",
                "lectures talks appearances",
                "public_activity",
                "academic_or_major_media",
            ),
            (
                "adaptations",
                "film television adaptations",
                "professional",
                "studio_or_database",
            ),
            (
                "causes",
                "charity philanthropy public causes",
                "public_activity",
                "foundation_or_ngo",
            ),
        ],
        "academic": [
            (
                "research",
                "research publications scholarship",
                "academic",
                "academic_institution",
            ),
            (
                "institution",
                "university department institution",
                "academic",
                "academic_institution",
            ),
            (
                "teaching",
                "teaching courses academic work",
                "academic",
                "academic_institution",
            ),
            (
                "awards",
                "academic awards honors",
                "academic",
                "award_body",
            ),
            (
                "lectures",
                "lectures talks conferences",
                "academic",
                "academic_institution_or_major_media",
            ),
            (
                "publications",
                "books papers publications",
                "academic",
                "academic_or_publisher",
            ),
        ],
        "artist": [
            (
                "works",
                "artworks exhibitions portfolio",
                "professional",
                "gallery_or_museum",
            ),
            (
                "awards",
                "art awards honors",
                "professional",
                "award_body",
            ),
            (
                "exhibitions",
                "exhibitions galleries museums",
                "professional",
                "gallery_or_museum",
            ),
            (
                "interviews",
                "interview artistic practice views",
                "interview",
                "major_media",
            ),
            (
                "collections",
                "museum collections acquisitions",
                "professional",
                "museum",
            ),
            (
                "causes",
                "charity philanthropy public causes",
                "public_activity",
                "foundation_or_ngo",
            ),
        ],
    }

    def _identity(self, task: ResearchTask) -> str:
        query = task.query_text.strip()

        if query.startswith('"') and '"' in query[1:]:
            return query.split('"', 2)[1]

        return query.split()[0]

    def _base_topic(self, task: ResearchTask) -> str:
        return (task.topic or task.query_type).replace("_", " ").strip()

    def _disambiguation_context(
        self,
        task: ResearchTask,
        identity_context: Optional[IdentityContext] = None,
    ) -> Optional[str]:
        """
        Build conservative identity context.

        Verified identity context takes precedence over the task-level
        profession. If no verified context is available, the existing
        profession-only fallback is preserved.

        Only explicitly supplied identity facts are used. No identity
        information is inferred or invented here.
        """
        if identity_context and identity_context.is_verified:
            parts: List[str] = []

            if identity_context.profession:
                parts.append(identity_context.profession.strip())

            if identity_context.nationality:
                parts.append(identity_context.nationality.strip())

            if identity_context.organization:
                parts.append(identity_context.organization.strip())

            if identity_context.location:
                parts.append(identity_context.location.strip())

            context = " ".join(
                part for part in parts if part
            ).strip()

            return context or None

        profession = (task.profession_context or "").strip()

        if profession:
            return profession

        return None

    def _build_query_with_context(
        self,
        person: str,
        query_text: str,
        disambiguation_context: Optional[str],
    ) -> str:
        if not disambiguation_context:
            return query_text

        return f"{query_text} {disambiguation_context}"

    def _add_variant(
        self,
        variants: List[QueryVariant],
        person: str,
        query_text: str,
        variant_type: str,
        source_focus: str,
        task: ResearchTask,
        priority_offset: int = 0,
        source_target: Optional[str] = None,
        identity_context: Optional[IdentityContext] = None,
    ) -> None:
        context = self._disambiguation_context(
            task=task,
            identity_context=identity_context,
        )

        contextual_query = self._build_query_with_context(
            person=person,
            query_text=query_text,
            disambiguation_context=context,
        )

        variants.append(
            QueryVariant(
                query_text=contextual_query,
                variant_type=variant_type,
                source_focus=source_focus,
                temporal_scope=task.temporal_scope,
                priority=max(task.priority - priority_offset, 1),
                source_target=source_target,
                disambiguation_context=context,
            )
        )

    def _add_profession_variants(
        self,
        variants: List[QueryVariant],
        person: str,
        task: ResearchTask,
        identity_context: Optional[IdentityContext] = None,
    ) -> None:
        profession = (task.profession_context or "").strip().lower()

        if (
            identity_context
            and identity_context.is_verified
            and identity_context.profession
        ):
            profession = identity_context.profession.strip().lower()

        if profession not in self.PROFESSION_QUERY_FAMILIES:
            return

        for index, (
            family_name,
            search_terms,
            source_focus,
            source_target,
        ) in enumerate(
            self.PROFESSION_QUERY_FAMILIES[profession]
        ):
            self._add_variant(
                variants=variants,
                person=person,
                query_text=f'"{person}" {search_terms}',
                variant_type=f"profession_{family_name}",
                source_focus=source_focus,
                task=task,
                priority_offset=3 + min(index, 3),
                source_target=source_target,
                identity_context=identity_context,
            )

    def generate(
        self,
        task: ResearchTask,
        identity_context: Optional[IdentityContext] = None,
    ) -> QueryBundle:
        """
        Generate targeted query variants for a research task.

        identity_context is optional for backward compatibility.

        If a verified IdentityContext is supplied, its explicitly verified
        profession, nationality, organization, and location may be used as
        conservative disambiguation context.

        If no verified context is supplied, the existing task-level
        profession fallback remains unchanged.
        """
        person = self._identity(task)
        topic = self._base_topic(task)

        variants: List[QueryVariant] = []

        self._add_variant(
            variants=variants,
            person=person,
            query_text=f'"{person}" {topic}',
            variant_type="canonical",
            source_focus="general",
            task=task,
            priority_offset=0,
            source_target="general_web",
            identity_context=identity_context,
        )

        self._add_variant(
            variants=variants,
            person=person,
            query_text=f'"{person}" "{topic}" official',
            variant_type="official",
            source_focus="official",
            task=task,
            priority_offset=1,
            source_target="official_source",
            identity_context=identity_context,
        )

        self._add_variant(
            variants=variants,
            person=person,
            query_text=f'"{person}" {topic} interview',
            variant_type="interview",
            source_focus="interview",
            task=task,
            priority_offset=2,
            source_target="major_media_or_interview",
            identity_context=identity_context,
        )

        self._add_profession_variants(
            variants=variants,
            person=person,
            task=task,
            identity_context=identity_context,
        )

        if task.temporal_scope and task.temporal_scope != "full_career":
            self._add_variant(
                variants=variants,
                person=person,
                query_text=f'"{person}" {topic} {task.temporal_scope}',
                variant_type="temporal",
                source_focus="historical",
                task=task,
                priority_offset=2,
                source_target="historical_sources",
                identity_context=identity_context,
            )

        return QueryBundle(
            task_id=task.task_id,
            variants=variants,
        )