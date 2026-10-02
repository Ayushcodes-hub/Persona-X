from statistics import mean
from typing import Iterable, Optional

from engine.analysis.dossier_schemas import (
    DossierFinding,
    DossierSection,
    DossierSynthesis,
)


class DossierSynthesizer:
    """
    Deterministic dossier assembly layer.

    This layer assembles already extracted and evidence-backed
    information. It does not invent facts or perform new research.
    """

    SECTION_ORDER = [
        "identity",
        "biography",
        "education",
        "career",
        "affiliations",
        "timeline",
        "statements",
        "initiatives",
        "achievements",
        "topics",
        "temporal_evolution",
        "potential_inconsistencies",
        "profession_analysis",
        "political_analysis",
        "limitations",
    ]

    def synthesize(
        self,
        person_name: str,
        canonical_name: Optional[str] = None,
        professions: Optional[Iterable[str]] = None,
        sections: Optional[Iterable[DossierSection]] = None,
        findings: Optional[Iterable[DossierFinding]] = None,
        source_count: int = 0,
        evidence_count: int = 0,
        political_analysis_included: bool = False,
        limitations: Optional[Iterable[str]] = None,
    ) -> DossierSynthesis:

        normalized_sections = self._order_sections(
            list(sections or [])
        )

        normalized_findings = list(findings or [])

        all_evidence_ids = set()
        all_source_ids = set()

        for section in normalized_sections:
            all_evidence_ids.update(section.evidence_ids)
            all_source_ids.update(section.source_ids)

        for finding in normalized_findings:
            all_evidence_ids.update(finding.evidence_ids)
            all_source_ids.update(finding.source_ids)

        effective_evidence_count = max(
            evidence_count,
            len(all_evidence_ids),
        )

        effective_source_count = max(
            source_count,
            len(all_source_ids),
        )

        completeness_score = self._completeness(
            normalized_sections
        )

        evidence_coverage_score = self._evidence_coverage(
            normalized_sections,
            normalized_findings,
        )

        confidence = self._overall_confidence(
            normalized_sections,
            normalized_findings,
        )

        executive_summary = self._build_summary(
            person_name=person_name,
            professions=list(professions or []),
            sections=normalized_sections,
            findings=normalized_findings,
            evidence_count=effective_evidence_count,
            source_count=effective_source_count,
        )

        return DossierSynthesis(
            person_name=person_name,
            canonical_name=canonical_name or person_name,
            profession=list(professions or []),
            executive_summary=executive_summary,
            sections=normalized_sections,
            findings=normalized_findings,
            source_count=effective_source_count,
            evidence_count=effective_evidence_count,
            completeness_score=completeness_score,
            evidence_coverage_score=evidence_coverage_score,
            confidence=confidence,
            political_analysis_included=political_analysis_included,
            limitations=list(limitations or []),
        )

    def _order_sections(
        self,
        sections: list[DossierSection],
    ) -> list[DossierSection]:

        position = {
            key: index
            for index, key in enumerate(self.SECTION_ORDER)
        }

        return sorted(
            sections,
            key=lambda section: position.get(
                section.key,
                len(self.SECTION_ORDER),
            ),
        )

    @classmethod
    def _completeness(
        cls,
        sections: list[DossierSection],
    ) -> float:

        if not sections:
            return 0.0

        expected = set(cls.SECTION_ORDER)

        present = {
            section.key
            for section in sections
            if section.content.strip()
        }

        return round(
            len(present & expected) / len(expected),
            4,
        )

    @staticmethod
    def _evidence_coverage(
        sections: list[DossierSection],
        findings: list[DossierFinding],
    ) -> float:

        total_items = len(sections) + len(findings)

        if total_items == 0:
            return 0.0

        supported_items = sum(
            1
            for item in [*sections, *findings]
            if item.evidence_ids or item.source_ids
        )

        return round(
            supported_items / total_items,
            4,
        )

    @staticmethod
    def _overall_confidence(
        sections: list[DossierSection],
        findings: list[DossierFinding],
    ) -> Optional[float]:

        values = []

        for section in sections:
            if section.confidence is not None:
                values.append(section.confidence)

        for finding in findings:
            if finding.confidence is not None:
                values.append(finding.confidence)

        if not values:
            return None

        return round(mean(values), 4)

    @staticmethod
    def _build_summary(
        person_name: str,
        professions: list[str],
        sections: list[DossierSection],
        findings: list[DossierFinding],
        evidence_count: int,
        source_count: int,
    ) -> str:

        profession_text = (
            ", ".join(professions)
            if professions
            else "profession not established"
        )

        supported_findings = sum(
            1
            for finding in findings
            if finding.evidence_ids or finding.source_ids
        )

        return (
            f"{person_name} is documented in PERSONA-X as "
            f"{profession_text}. The dossier contains "
            f"{len(sections)} structured sections, "
            f"{supported_findings} evidence-backed findings, "
            f"{evidence_count} evidence records, and "
            f"{source_count} sources. "
            "Conclusions are limited to information represented "
            "in the underlying evidence set."
        )