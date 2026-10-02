from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.models import Base, Evidence, Person, Source
from backend.app.services.evidence_extraction import EvidenceExtractionService


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    return engine


def create_test_entities(db):
    person = Person(
        canonical_name="PERSONA-X Evidence Test Person",
        primary_profession="test",
        identity_confidence=1.0,
        identity_status="resolved",
    )

    source = Source(
        url="https://example.com/persona-x-evidence",
        title="PERSONA-X Evidence Test",
        publisher="Example",
        source_type="general_web",
        source_tier=4,
        reliability_score=0.5,
        is_verified=False,
    )

    db.add_all([person, source])
    db.commit()

    db.refresh(person)
    db.refresh(source)

    return person, source


def test_create_evidence():
    engine = create_test_db()
    db = Session(engine)

    person, source = create_test_entities(db)

    service = EvidenceExtractionService()

    evidence = service.create_evidence(
        db=db,
        person=person,
        source=source,
        extracted_text="   PERSONA-X documented public statement.   ",
        evidence_type="public_statement",
        normalized_claim="PERSONA-X made a public statement.",
        source_locator="paragraph 4",
        confidence=0.85,
    )

    assert evidence.id is not None
    assert evidence.person_id == person.id
    assert evidence.source_id == source.id
    assert evidence.evidence_type == "public_statement"
    assert evidence.extracted_text == "PERSONA-X documented public statement."
    assert evidence.normalized_claim == (
        "PERSONA-X made a public statement."
    )
    assert evidence.source_locator == "paragraph 4"
    assert evidence.confidence == 0.85
    assert evidence.verification_status == "unverified"
    assert evidence.extraction_method == "deterministic"

    db.close()
    engine.dispose()


def test_confidence_is_bounded():
    engine = create_test_db()
    db = Session(engine)

    person, source = create_test_entities(db)
    service = EvidenceExtractionService()

    low = service.create_evidence(
        db=db,
        person=person,
        source=source,
        extracted_text="Low confidence evidence.",
        evidence_type="general",
        confidence=-5.0,
    )

    high = service.create_evidence(
        db=db,
        person=person,
        source=source,
        extracted_text="High confidence evidence.",
        evidence_type="general",
        confidence=5.0,
    )

    assert low.confidence == 0.0
    assert high.confidence == 1.0

    db.close()
    engine.dispose()


def test_empty_evidence_is_rejected():
    engine = create_test_db()
    db = Session(engine)

    person, source = create_test_entities(db)
    service = EvidenceExtractionService()

    with pytest.raises(ValueError, match="Evidence text cannot be empty"):
        service.create_evidence(
            db=db,
            person=person,
            source=source,
            extracted_text="   ",
            evidence_type="general",
        )

    db.close()
    engine.dispose()


def test_evidence_type_is_required():
    engine = create_test_db()
    db = Session(engine)

    person, source = create_test_entities(db)
    service = EvidenceExtractionService()

    with pytest.raises(ValueError, match="Evidence type is required"):
        service.create_evidence(
            db=db,
            person=person,
            source=source,
            extracted_text="Valid evidence.",
            evidence_type="   ",
        )

    db.close()
    engine.dispose()


def test_duplicate_evidence_is_not_created():
    engine = create_test_db()
    db = Session(engine)

    person, source = create_test_entities(db)
    service = EvidenceExtractionService()

    first = service.create_if_new(
        db=db,
        person=person,
        source=source,
        extracted_text="The same evidence appears twice.",
        evidence_type="documented_fact",
        confidence=0.9,
    )

    second = service.create_if_new(
        db=db,
        person=person,
        source=source,
        extracted_text="  The same evidence appears twice.  ",
        evidence_type="documented_fact",
        confidence=0.9,
    )

    total = (
        db.query(Evidence)
        .filter(Evidence.person_id == person.id)
        .count()
    )

    assert first.id == second.id
    assert total == 1

    db.close()
    engine.dispose()


def test_event_date_and_model_metadata_are_preserved():
    engine = create_test_db()
    db = Session(engine)

    person, source = create_test_entities(db)
    service = EvidenceExtractionService()

    event_date = datetime(2026, 9, 21)

    evidence = service.create_evidence(
        db=db,
        person=person,
        source=source,
        extracted_text="A dated public event.",
        evidence_type="timeline_event",
        event_date=event_date,
        extraction_method="llm_structured_extraction",
        extraction_model="openai/gpt-oss-120b",
    )

    assert evidence.event_date == event_date
    assert evidence.extraction_method == "llm_structured_extraction"
    assert evidence.extraction_model == "openai/gpt-oss-120b"

    db.close()
    engine.dispose()