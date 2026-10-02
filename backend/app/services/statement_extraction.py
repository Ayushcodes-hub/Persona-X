from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.models.evidence import Evidence
from backend.app.models.person import Person
from backend.app.models.source import Source
from backend.app.models.statement import Statement


class StatementExtractionService:
    """
    Create traceable public statements from source-grounded evidence.

    This service records statements supplied by the research pipeline.
    It does not invent quotations or attribute unsupported statements.
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

    def create_statement(
        self,
        db: Session,
        person: Person,
        source: Source,
        evidence: Evidence,
        text: str,
        statement_type: str = "public_statement",
        paraphrase: Optional[str] = None,
        topic: Optional[str] = None,
        context: Optional[str] = None,
        statement_date: Optional[datetime] = None,
        attribution_status: str = "unverified",
        confidence: float = 0.0,
    ) -> Statement:

        if evidence.person_id != person.id:
            raise ValueError(
                "Evidence does not belong to the supplied Person."
            )

        if evidence.source_id != source.id:
            raise ValueError(
                "Evidence does not belong to the supplied Source."
            )

        normalized_text = self.normalize_text(text)

        if not normalized_text:
            raise ValueError("Statement text cannot be empty.")

        if not statement_type or not statement_type.strip():
            raise ValueError("Statement type is required.")

        confidence = self.validate_confidence(confidence)

        statement = Statement(
            person_id=person.id,
            source_id=source.id,
            evidence_id=evidence.id,
            statement_type=statement_type.strip(),
            text=normalized_text,
            paraphrase=self.normalize_text(paraphrase),
            topic=self.normalize_text(topic),
            context=self.normalize_text(context),
            statement_date=statement_date,
            attribution_status=attribution_status,
            confidence=confidence,
        )

        db.add(statement)
        db.commit()
        db.refresh(statement)

        return statement

    def find_duplicate(
        self,
        db: Session,
        person_id: int,
        source_id: int,
        text: str,
    ) -> Optional[Statement]:

        normalized_text = self.normalize_text(text)

        if not normalized_text:
            return None

        return (
            db.query(Statement)
            .filter(
                Statement.person_id == person_id,
                Statement.source_id == source_id,
                Statement.text == normalized_text,
            )
            .first()
        )

    def create_if_new(
        self,
        db: Session,
        person: Person,
        source: Source,
        evidence: Evidence,
        text: str,
        statement_type: str = "public_statement",
        paraphrase: Optional[str] = None,
        topic: Optional[str] = None,
        context: Optional[str] = None,
        statement_date: Optional[datetime] = None,
        attribution_status: str = "unverified",
        confidence: float = 0.0,
    ) -> Statement:

        existing = self.find_duplicate(
            db=db,
            person_id=person.id,
            source_id=source.id,
            text=text,
        )

        if existing:
            return existing

        return self.create_statement(
            db=db,
            person=person,
            source=source,
            evidence=evidence,
            text=text,
            statement_type=statement_type,
            paraphrase=paraphrase,
            topic=topic,
            context=context,
            statement_date=statement_date,
            attribution_status=attribution_status,
            confidence=confidence,
        )