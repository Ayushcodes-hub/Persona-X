from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.models.evidence import Evidence
from backend.app.models.person import Person
from backend.app.models.source import Source


class EvidenceExtractionService:
    """Create traceable evidence records from acquired source material."""

    DEFAULT_EXTRACTION_METHOD = "deterministic"

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""

        return " ".join(text.split()).strip()

    def validate_confidence(self, confidence: float) -> float:
        if confidence < 0.0:
            return 0.0

        if confidence > 1.0:
            return 1.0

        return confidence

    def create_evidence(
        self,
        db: Session,
        person: Person,
        source: Source,
        extracted_text: str,
        evidence_type: str,
        normalized_claim: Optional[str] = None,
        source_locator: Optional[str] = None,
        event_date: Optional[datetime] = None,
        confidence: float = 0.0,
        extraction_method: str = DEFAULT_EXTRACTION_METHOD,
        extraction_model: Optional[str] = None,
        verification_status: str = "unverified",
    ) -> Evidence:
        normalized_text = self.normalize_text(extracted_text)

        if not normalized_text:
            raise ValueError("Evidence text cannot be empty.")

        if not evidence_type or not evidence_type.strip():
            raise ValueError("Evidence type is required.")

        confidence = self.validate_confidence(confidence)

        evidence = Evidence(
            person_id=person.id,
            source_id=source.id,
            evidence_type=evidence_type.strip(),
            verification_status=verification_status,
            extracted_text=normalized_text,
            normalized_claim=(
                self.normalize_text(normalized_claim)
                if normalized_claim
                else None
            ),
            source_locator=(
                source_locator.strip()
                if source_locator
                else None
            ),
            event_date=event_date,
            confidence=confidence,
            extraction_method=extraction_method,
            extraction_model=extraction_model,
        )

        db.add(evidence)
        db.commit()
        db.refresh(evidence)

        return evidence

    def find_duplicate(
        self,
        db: Session,
        person_id: int,
        source_id: int,
        extracted_text: str,
    ) -> Optional[Evidence]:
        normalized_text = self.normalize_text(extracted_text)

        if not normalized_text:
            return None

        return (
            db.query(Evidence)
            .filter(
                Evidence.person_id == person_id,
                Evidence.source_id == source_id,
                Evidence.extracted_text == normalized_text,
            )
            .first()
        )

    def create_if_new(
        self,
        db: Session,
        person: Person,
        source: Source,
        extracted_text: str,
        evidence_type: str,
        normalized_claim: Optional[str] = None,
        source_locator: Optional[str] = None,
        event_date: Optional[datetime] = None,
        confidence: float = 0.0,
        extraction_method: str = DEFAULT_EXTRACTION_METHOD,
        extraction_model: Optional[str] = None,
        verification_status: str = "unverified",
    ) -> Evidence:
        existing = self.find_duplicate(
            db=db,
            person_id=person.id,
            source_id=source.id,
            extracted_text=extracted_text,
        )

        if existing:
            return existing

        return self.create_evidence(
            db=db,
            person=person,
            source=source,
            extracted_text=extracted_text,
            evidence_type=evidence_type,
            normalized_claim=normalized_claim,
            source_locator=source_locator,
            event_date=event_date,
            confidence=confidence,
            extraction_method=extraction_method,
            extraction_model=extraction_model,
            verification_status=verification_status,
        )