from typing import Iterable, List

from engine.political.schemas import PoliticalEvidence


QUALIFYING_TYPES = {
    "self_identification",
    "party_affiliation",
    "policy_statement",
    "political_action",
    "legislative_record",
    "campaign_activity",
    "political_office",
    "public_advocacy",
    "political_interview",
    "institutional_record",
}


DIRECT_TYPES = {
    "self_identification",
    "party_affiliation",
    "policy_statement",
    "political_action",
    "legislative_record",
    "campaign_activity",
    "political_office",
    "public_advocacy",
    "political_interview",
}


class PoliticalEvidenceClassifier:
    def normalize(self, evidence: PoliticalEvidence) -> PoliticalEvidence:
        evidence_type = evidence.evidence_type.strip().lower()

        position = (
            evidence.position.strip().lower()
            if evidence.position
            else None
        )

        attribution = (
            evidence.attribution_status.strip().lower()
            if evidence.attribution_status
            else "unknown"
        )

        verification = (
            evidence.verification_status.strip().lower()
            if evidence.verification_status
            else "unverified"
        )

        return PoliticalEvidence(
            evidence_type=evidence_type,
            text=evidence.text.strip(),
            topic=evidence.topic,
            issue=evidence.issue,
            position=position,
            evidence_id=evidence.evidence_id,
            source_id=evidence.source_id,
            statement_id=evidence.statement_id,
            event_date=evidence.event_date,
            source_tier=evidence.source_tier,
            verification_status=verification,
            attribution_status=attribution,
            confidence=max(0.0, min(1.0, evidence.confidence)),
        )

    def classify(
        self,
        evidence: Iterable[PoliticalEvidence],
    ) -> List[PoliticalEvidence]:
        normalized = []

        for item in evidence:
            normalized.append(self.normalize(item))

        return normalized

    def is_qualifying(
        self,
        evidence: PoliticalEvidence,
    ) -> bool:
        return (
            evidence.evidence_type in QUALIFYING_TYPES
            and evidence.text.strip() != ""
            and evidence.confidence >= 0.60
        )

    def is_direct(
        self,
        evidence: PoliticalEvidence,
    ) -> bool:
        return evidence.evidence_type in DIRECT_TYPES

    def qualifying_evidence(
        self,
        evidence: Iterable[PoliticalEvidence],
    ) -> List[PoliticalEvidence]:
        return [
            item
            for item in evidence
            if self.is_qualifying(item)
        ]