from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models import Base
from backend.app.models.evidence import Evidence
from backend.app.models.initiative import Initiative
from backend.app.models.person import Person
from backend.app.services.initiative_extraction import (
    InitiativeExtractionService,
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
        extracted_text=(
            "Test evidence passage for initiative extraction."
        ),
        confidence=1.0,
    )

    db.add(value)
    db.commit()
    db.refresh(value)

    return value


def test_create_initiative(db, person, evidence):
    service = InitiativeExtractionService()

    initiative = service.create_initiative(
        db=db,
        person=person,
        evidence=evidence,
        name="Example Initiative",
        initiative_type="public_program",
        description="A documented initiative.",
        objective="Improve public outcomes.",
        lifecycle_stage="implemented",
        start_date=datetime(2020, 1, 1),
        organization="Example Organization",
        location="Bengaluru",
        outcome="Program implemented.",
        evaluation="Evaluation documented.",
        evidence_confidence=0.9,
        verification_status="partially_verified",
    )

    assert initiative.id is not None
    assert initiative.person_id == person.id
    assert initiative.evidence_id == evidence.id
    assert initiative.name == "Example Initiative"
    assert initiative.initiative_type == "public_program"
    assert initiative.lifecycle_stage == "implemented"
    assert initiative.organization == "Example Organization"
    assert initiative.location == "Bengaluru"
    assert initiative.outcome == "Program implemented."
    assert initiative.evaluation == "Evaluation documented."
    assert initiative.evidence_confidence == 0.9
    assert initiative.verification_status == "partially_verified"


def test_text_is_normalized(db, person, evidence):
    service = InitiativeExtractionService()

    initiative = service.create_initiative(
        db=db,
        person=person,
        evidence=evidence,
        name="   Example    Initiative   ",
        initiative_type="  public_program ",
        description="  A   documented initiative. ",
        objective=" Improve   public outcomes. ",
        organization=" Example   Organization ",
        location=" Bengaluru ",
    )

    assert initiative.name == "Example Initiative"
    assert initiative.initiative_type == "public_program"
    assert initiative.description == "A documented initiative."
    assert initiative.objective == "Improve public outcomes."
    assert initiative.organization == "Example Organization"
    assert initiative.location == "Bengaluru"


def test_confidence_is_clamped(db, person, evidence):
    service = InitiativeExtractionService()

    low = service.create_initiative(
        db=db,
        person=person,
        evidence=evidence,
        name="Low Confidence Initiative",
        initiative_type="project",
        evidence_confidence=-5,
    )

    high = service.create_initiative(
        db=db,
        person=person,
        evidence=evidence,
        name="High Confidence Initiative",
        initiative_type="project",
        evidence_confidence=5,
    )

    assert low.evidence_confidence == 0.0
    assert high.evidence_confidence == 1.0


def test_duplicate_initiative_is_not_created(
    db,
    person,
    evidence,
):
    service = InitiativeExtractionService()

    first = service.create_if_new(
        db=db,
        person=person,
        evidence=evidence,
        name="Example Initiative",
        initiative_type="project",
    )

    second = service.create_if_new(
        db=db,
        person=person,
        evidence=evidence,
        name="  Example   Initiative ",
        initiative_type="project",
    )

    assert first.id == second.id

    count = db.query(Initiative).count()

    assert count == 1


def test_evidence_must_belong_to_person(db, person):
    service = InitiativeExtractionService()

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
        service.create_initiative(
            db=db,
            person=person,
            evidence=evidence,
            name="Invalid Initiative",
            initiative_type="project",
        )


def test_invalid_lifecycle_stage_is_rejected(
    db,
    person,
    evidence,
):
    service = InitiativeExtractionService()

    with pytest.raises(
        ValueError,
        match="Invalid lifecycle stage",
    ):
        service.create_initiative(
            db=db,
            person=person,
            evidence=evidence,
            name="Invalid Lifecycle Initiative",
            initiative_type="project",
            lifecycle_stage="unknown_stage",
        )


def test_invalid_date_range_is_rejected(
    db,
    person,
    evidence,
):
    service = InitiativeExtractionService()

    with pytest.raises(
        ValueError,
        match="end date cannot be earlier",
    ):
        service.create_initiative(
            db=db,
            person=person,
            evidence=evidence,
            name="Invalid Date Initiative",
            initiative_type="project",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2024, 1, 1),
        )


def test_empty_name_is_rejected(db, person, evidence):
    service = InitiativeExtractionService()

    with pytest.raises(
        ValueError,
        match="Initiative name cannot be empty",
    ):
        service.create_initiative(
            db=db,
            person=person,
            evidence=evidence,
            name="   ",
            initiative_type="project",
        )