from typing import List

from engine.analysis.dossier_schemas import (
    DossierSection,
    DossierSynthesis,
)


class DossierNarrator:
    """
    Produces a conservative readable representation of a structured dossier.

    This layer intentionally operates on already structured information.
    It does not perform new factual research.
    """

    def render(self, dossier: DossierSynthesis) -> str:
        parts: List[str] = []

        parts.append(
            f"# {dossier.canonical_name or dossier.person_name}"
        )

        if dossier.profession:
            parts.append(
                f"**Profession:** {', '.join(dossier.profession)}"
            )

        if dossier.executive_summary:
            parts.append(
                "## Executive Summary\n"
                + dossier.executive_summary
            )

        for section in dossier.sections:
            if not section.content.strip():
                continue

            parts.append(
                f"## {section.title}\n"
                f"{section.content}"
            )

        if dossier.findings:
            parts.append("## Evidence-Backed Findings")

            for finding in dossier.findings:
                parts.append(
                    f"### {finding.title}\n"
                    f"{finding.description}"
                )

        if dossier.limitations:
            parts.append("## Limitations")

            for limitation in dossier.limitations:
                parts.append(f"- {limitation}")

        return "\n\n".join(parts)