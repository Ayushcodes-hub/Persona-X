from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.models.evidence import Evidence
from backend.app.models.initiative import Initiative
from backend.app.models.person import Person


class InitiativeExtractionService:
    """
    Create traceable initiatives from source-grounded evidence.

    This service records initiatives supplied by the research pipeline.
    It does not independently assert that an initiative succeeded,
    was implemented, or produced a particular outcome.
    """

    VALID_LIFECYCLE_STAGES = {
        "proposed",
        "announced",
        "launched",
        "implemented",
        "completed",
        "evaluated",
    }

    def normalize_text(
        self,
        value: Optional[str],
    ) -> Optional[str]:
        if value is None:
            return None

        normalized = " ".join(value.split()).strip()
        return normalized or None

    def validate_confidence(
        self,
        confidence: float,
    ) -> float:
        if confidence is None:
            return 0.0

        return max(0.0, min(1.0, float(confidence)))

    def validate_lifecycle_stage(
        self,
        lifecycle_stage: str,
    ) -> str:
        normalized = self.normalize_text(lifecycle_stage)

        if not normalized:
            raise ValueError(
                "Lifecycle stage cannot be empty."
            )

        normalized = normalized.lower()

        if normalized not in self.VALID_LIFECYCLE_STAGES:
            raise ValueError(
                f"Invalid lifecycle stage: {normalized}"
            )

        return normalized

    def create_initiative(
        self,
        db: Session,
        person: Person,
        evidence: Evidence,
        name: str,
        initiative_type: str,
        description: Optional[str] = None,
        objective: Optional[str] = None,
        lifecycle_stage: str = "proposed",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        organization: Optional[str] = None,
        location: Optional[str] = None,
        outcome: Optional[str] = None,
        evaluation: Optional[str] = None,
        evidence_confidence: float = 0.0,
        verification_status: str = "unverified",
    ) -> Initiative:

        if evidence.person_id != person.id:
            raise ValueError(
                "Evidence does not belong to the supplied Person."
            )

        if not name or not name.strip():
            raise ValueError(
                "Initiative name cannot be empty."
            )

        if not initiative_type or not initiative_type.strip():
            raise ValueError(
                "Initiative type cannot be empty."
            )

        if start_date and end_date and end_date < start_date:
            raise ValueError(
                "Initiative end date cannot be earlier than start date."
            )

        normalized_stage = self.validate_lifecycle_stage(
            lifecycle_stage
        )

        normalized_verification = (
            self.normalize_text(verification_status)
            or "unverified"
        )

        initiative = Initiative(
            person_id=person.id,
            evidence_id=evidence.id,
            name=self.normalize_text(name),
            initiative_type=self.normalize_text(
                initiative_type
            ),
            description=self.normalize_text(description),
            objective=self.normalize_text(objective),
            lifecycle_stage=normalized_stage,
            start_date=start_date,
            end_date=end_date,
            organization=self.normalize_text(organization),
            location=self.normalize_text(location),
            outcome=self.normalize_text(outcome),
            evaluation=self.normalize_text(evaluation),
            evidence_confidence=self.validate_confidence(
                evidence_confidence
            ),
            verification_status=normalized_verification,
        )

        db.add(initiative)
        db.commit()
        db.refresh(initiative)

        return initiative

    def find_duplicate(
        self,
        db: Session,
        person_id: int,
        evidence_id: int,
        name: str,
    ) -> Optional[Initiative]:

        normalized_name = self.normalize_text(name)

        return (
            db.query(Initiative)
            .filter(
                Initiative.person_id == person_id,
                Initiative.evidence_id == evidence_id,
                Initiative.name == normalized_name,
            )
            .first()
        )

    def create_if_new(
        self,
        db: Session,
        person: Person,
        evidence: Evidence,
        name: str,
        initiative_type: str,
        description: Optional[str] = None,
        objective: Optional[str] = None,
        lifecycle_stage: str = "proposed",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        organization: Optional[str] = None,
        location: Optional[str] = None,
        outcome: Optional[str] = None,
        evaluation: Optional[str] = None,
        evidence_confidence: float = 0.0,
        verification_status: str = "unverified",
    ) -> Initiative:

        existing = self.find_duplicate(
            db=db,
            person_id=person.id,
            evidence_id=evidence.id,
            name=name,
        )

        if existing:
            return existing

        return self.create_initiative(
            db=db,
            person=person,
            evidence=evidence,
            name=name,
            initiative_type=initiative_type,
            description=description,
            objective=objective,
            lifecycle_stage=lifecycle_stage,
            start_date=start_date,
            end_date=end_date,
            organization=organization,
            location=location,
            outcome=outcome,
            evaluation=evaluation,
            evidence_confidence=evidence_confidence,
            verification_status=verification_status,
        )