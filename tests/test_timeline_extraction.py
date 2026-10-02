from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base
from backend.app.models.evidence import Evidence
from backend.app.models.person import Person
from backend.app.services.timeline_extraction import (
    TimelineExtractionService,
)


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def person(db):
    value = Person(
        canonical_name="Test Person",
        identity_status="resolved",
        identity_confidence=1.0,
    )
    db.add(value)
    db.commit()
    db.refresh(value)
    return value


@pytest.fixture
def evidence(db, person):
    value = Evidence(
        person_id=person.id,
        source_id=1,
        evidence_type="source_passage",
        verification_status="unverified",
        extracted_text="Test evidence passage for timeline extraction.",
        confidence=1.0,
    )
    db.add(value)
    db.commit()
    db.refresh(value)
    return value


def test_create_timeline_event(db, person, evidence):
    service = TimelineExtractionService()

    event = service.create_event(
        db=db,
        person=person,
        evidence=evidence,
        event_type="career",
        title="Joined Example Organization",
        description="The person joined Example Organization.",
        start_date=datetime(2020, 1, 1),
        organization="Example Organization",
        location="Bengaluru",
        status="completed",
        confidence=0.9,
    )

    assert event.id is not None
    assert event.person_id == person.id
    assert event.evidence_id == evidence.id
    assert event.event_type == "career"
    assert event.title == "Joined Example Organization"
    assert event.organization == "Example Organization"
    assert event.location == "Bengaluru"
    assert event.status == "completed"
    assert event.confidence == 0.9


def test_text_is_normalized(db, person, evidence):
    service = TimelineExtractionService()

    event = service.create_event(
        db=db,
        person=person,
        evidence=evidence,
        event_type="  career  ",
        title="   Joined    Example   Organization   ",
        description="  Person   joined   organization. ",
        organization="  Example   Organization ",
        location="  Bengaluru ",
        status="  completed ",
    )

    assert event.event_type == "career"
    assert event.title == "Joined Example Organization"
    assert event.description == "Person joined organization."
    assert event.organization == "Example Organization"
    assert event.location == "Bengaluru"
    assert event.status == "completed"


def test_confidence_is_clamped(db, person, evidence):
    service = TimelineExtractionService()

    low = service.create_event(
        db=db,
        person=person,
        evidence=evidence,
        event_type="award",
        title="Received Award",
        confidence=-5,
    )

    high = service.create_event(
        db=db,
        person=person,
        evidence=evidence,
        event_type="award",
        title="Received Another Award",
        confidence=5,
    )

    assert low.confidence == 0.0
    assert high.confidence == 1.0


def test_duplicate_event_is_not_created(db, person, evidence):
    service = TimelineExtractionService()

    first = service.create_if_new(
        db=db,
        person=person,
        evidence=evidence,
        event_type="career",
        title="Joined Example Organization",
        start_date=datetime(2020, 1, 1),
    )

    second = service.create_if_new(
        db=db,
        person=person,
        evidence=evidence,
        event_type="career",
        title="  Joined   Example Organization ",
        start_date=datetime(2020, 1, 1),
    )

    assert first.id == second.id

    count = db.query(
        __import__(
            "backend.app.models.timeline",
            fromlist=["TimelineEvent"],
        ).TimelineEvent
    ).count()

    assert count == 1


def test_evidence_must_belong_to_person(db, person):
    service = TimelineExtractionService()

    other_person = Person(
        canonical_name="Other Person",
        identity_status="resolved",
        identity_confidence=1.0,
    )

    db.add(other_person)
    db.commit()
    db.refresh(other_person)

    evidence = Evidence(
        person_id=other_person.id,
        source_id=1,
        evidence_type="source_passage",
        verification_status="unverified",
        extracted_text="Evidence belonging to another person.",
        confidence=1.0,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    with pytest.raises(
        ValueError,
        match="Evidence does not belong to the supplied Person",
    ):
        service.create_event(
            db=db,
            person=person,
            evidence=evidence,
            event_type="career",
            title="Invalid Event",
        )


def test_invalid_date_range_is_rejected(db, person, evidence):
    service = TimelineExtractionService()

    with pytest.raises(
        ValueError,
        match="end date cannot be earlier",
    ):
        service.create_event(
            db=db,
            person=person,
            evidence=evidence,
            event_type="career",
            title="Invalid Date Event",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2024, 1, 1),
        )


def test_empty_event_title_is_rejected(db, person, evidence):
    service = TimelineExtractionService()

    with pytest.raises(
        ValueError,
        match="Timeline event title cannot be empty",
    ):
        service.create_event(
            db=db,
            person=person,
            evidence=evidence,
            event_type="career",
            title="   ",
        )