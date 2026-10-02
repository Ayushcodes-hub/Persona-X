from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.models.evidence import Evidence
from backend.app.models.person import Person
from backend.app.models.timeline import TimelineEvent


class TimelineExtractionService:
    """
    Create traceable timeline events from source-grounded evidence.

    This service validates relationships and stores timeline events.
    It does not invent dates, events, organizations, or historical facts.
    """

    def normalize_text(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        normalized = " ".join(value.split()).strip()
        return normalized or None

    def validate_confidence(self, confidence: float) -> float:
        if confidence is None:
            return 0.0

        return max(0.0, min(1.0, float(confidence)))

    def create_event(
        self,
        db: Session,
        person: Person,
        evidence: Evidence,
        event_type: str,
        title: str,
        description: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        organization: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
        confidence: float = 0.0,
    ) -> TimelineEvent:
        if evidence.person_id != person.id:
            raise ValueError(
                "Evidence does not belong to the supplied Person."
            )

        if not event_type or not event_type.strip():
            raise ValueError("Event type cannot be empty.")

        if not title or not title.strip():
            raise ValueError("Timeline event title cannot be empty.")

        if start_date and end_date and end_date < start_date:
            raise ValueError(
                "Timeline event end date cannot be earlier than start date."
            )

        event = TimelineEvent(
            person_id=person.id,
            event_type=self.normalize_text(event_type),
            title=self.normalize_text(title),
            description=self.normalize_text(description),
            start_date=start_date,
            end_date=end_date,
            organization=self.normalize_text(organization),
            location=self.normalize_text(location),
            status=self.normalize_text(status) or "documented",
            confidence=self.validate_confidence(confidence),
            evidence_id=evidence.id,
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return event

    def find_duplicate(
        self,
        db: Session,
        person_id: int,
        evidence_id: int,
        title: str,
    ) -> Optional[TimelineEvent]:
        normalized_title = self.normalize_text(title)

        return (
            db.query(TimelineEvent)
            .filter(
                TimelineEvent.person_id == person_id,
                TimelineEvent.evidence_id == evidence_id,
                TimelineEvent.title == normalized_title,
            )
            .first()
        )

    def create_if_new(
        self,
        db: Session,
        person: Person,
        evidence: Evidence,
        event_type: str,
        title: str,
        description: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        organization: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[str] = None,
        confidence: float = 0.0,
    ) -> TimelineEvent:
        existing = self.find_duplicate(
            db=db,
            person_id=person.id,
            evidence_id=evidence.id,
            title=title,
        )

        if existing:
            return existing

        return self.create_event(
            db=db,
            person=person,
            evidence=evidence,
            event_type=event_type,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            organization=organization,
            location=location,
            status=status,
            confidence=confidence,
        )