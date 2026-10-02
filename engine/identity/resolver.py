import re
from typing import Iterable, List

from engine.identity.schemas import IdentityCandidate, IdentityResolution


class IdentityResolver:
    """Deterministic identity-resolution foundation.

    This layer does not invent identity facts. It scores candidates using
    explicitly supplied evidence and leaves web discovery to later stages.
    """

    def normalize_name(self, name: str) -> str:
        name = name.strip().lower()
        name = re.sub(r"\\s+", " ", name)
        return name

    def score_candidate(
        self,
        query_name: str,
        candidate: IdentityCandidate,
    ) -> IdentityCandidate:
        query = self.normalize_name(query_name)
        candidate_name = self.normalize_name(candidate.name)

        score = 0.0
        reasons: List[str] = []

        if query == candidate_name:
            score += 0.70
            reasons.append("exact_name_match")
        elif query in candidate_name or candidate_name in query:
            score += 0.40
            reasons.append("partial_name_match")

        if candidate.profession:
            score += 0.05
            reasons.append("profession_available")

        if candidate.nationality:
            score += 0.05
            reasons.append("nationality_available")

        if candidate.organization:
            score += 0.05
            reasons.append("organization_available")

        if candidate.birth_date:
            score += 0.05
            reasons.append("birth_date_available")

        if candidate.source_url:
            score += 0.05
            reasons.append("source_url_available")

        if candidate.location:
            score += 0.05
            reasons.append("location_available")

        candidate.match_score = min(score, 1.0)
        candidate.confidence = candidate.match_score
        candidate.reasons = reasons
        return candidate

    def resolve(
        self,
        query_name: str,
        candidates: Iterable[IdentityCandidate],
    ) -> IdentityResolution:
        scored = [self.score_candidate(query_name, c) for c in candidates]
        scored.sort(key=lambda c: c.match_score, reverse=True)

        if not scored:
            return IdentityResolution(
                query_name=query_name,
                status="unresolved",
                confidence=0.0,
                ambiguity_notes="No identity candidates were supplied.",
            )

        top = scored[0]
        second = scored[1] if len(scored) > 1 else None

        if top.match_score < 0.75:
            status = "needs_review"
            notes = "Top candidate does not meet the automatic resolution threshold."
        elif second and (top.match_score - second.match_score) < 0.10:
            status = "ambiguous"
            notes = "Top candidates are too close in score for automatic resolution."
        else:
            status = "resolved"
            notes = None

        return IdentityResolution(
            query_name=query_name,
            status=status,
            confidence=top.confidence,
            canonical_name=top.name if status == "resolved" else None,
            candidates=scored,
            ambiguity_notes=notes,
        )
