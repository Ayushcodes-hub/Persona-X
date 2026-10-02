from typing import Optional

from sqlalchemy.orm import Session

from backend.app.models.claim import Claim
from backend.app.models.evidence import Evidence
from backend.app.models.person import Person


class ClaimExtractionService:
    """
    Create structured claims that remain directly traceable
    to source-grounded evidence.

    This service does not infer or invent claims.
    The caller must provide the claim proposition explicitly.
    """

    def normalize_text(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = " ".join(value.split()).strip()

        return normalized or None

    def validate_confidence(self, confidence: float) -> float:
        if confidence < 0.0:
            return 0.0

        if confidence > 1.0:
            return 1.0

        return confidence

    def create_claim(
        self,
        db: Session,
        person: Person,
        evidence: Evidence,
        claim_type: str,
        claim_text: str,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_value: Optional[str] = None,
        topic: Optional[str] = None,
        verification_status: str = "unverified",
        confidence: float = 0.0,
        analyst_notes: Optional[str] = None,
    ) -> Claim:

        if evidence.person_id != person.id:
            raise ValueError(
                "Evidence does not belong to the supplied Person."
            )

        if not claim_type or not claim_type.strip():
            raise ValueError("Claim type is required.")

        normalized_claim_text = self.normalize_text(claim_text)

        if not normalized_claim_text:
            raise ValueError("Claim text cannot be empty.")

        confidence = self.validate_confidence(confidence)

        claim = Claim(
            person_id=person.id,
            evidence_id=evidence.id,
            claim_type=claim_type.strip(),
            claim_text=normalized_claim_text,
            topic=self.normalize_text(topic),
            subject=self.normalize_text(subject),
            predicate=self.normalize_text(predicate),
            object_value=self.normalize_text(object_value),
            verification_status=verification_status,
            confidence=confidence,
            analyst_notes=self.normalize_text(analyst_notes),
        )

        db.add(claim)
        db.commit()
        db.refresh(claim)

        return claim

    def find_duplicate(
        self,
        db: Session,
        person_id: int,
        evidence_id: int,
        claim_text: str,
    ) -> Optional[Claim]:

        normalized_claim_text = self.normalize_text(claim_text)

        if not normalized_claim_text:
            return None

        return (
            db.query(Claim)
            .filter(
                Claim.person_id == person_id,
                Claim.evidence_id == evidence_id,
                Claim.claim_text == normalized_claim_text,
            )
            .first()
        )

    def create_if_new(
        self,
        db: Session,
        person: Person,
        evidence: Evidence,
        claim_type: str,
        claim_text: str,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        object_value: Optional[str] = None,
        topic: Optional[str] = None,
        verification_status: str = "unverified",
        confidence: float = 0.0,
        analyst_notes: Optional[str] = None,
    ) -> Claim:

        existing = self.find_duplicate(
            db=db,
            person_id=person.id,
            evidence_id=evidence.id,
            claim_text=claim_text,
        )

        if existing:
            return existing

        return self.create_claim(
            db=db,
            person=person,
            evidence=evidence,
            claim_type=claim_type,
            claim_text=claim_text,
            subject=subject,
            predicate=predicate,
            object_value=object_value,
            topic=topic,
            verification_status=verification_status,
            confidence=confidence,
            analyst_notes=analyst_notes,
        )