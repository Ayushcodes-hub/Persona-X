from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import pytest

from backend.app.models import (
    Base,
    Evidence,
    Person,
    Source,
    Statement,
)
from backend.app.services.statement_extraction import (
    StatementExtractionService,
)


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    return engine


def create_entities(db):
    person = Person(
        canonical_name="PERSONA-X Statement Test",
        primary_profession="test",
        identity_confidence=1.0,
        identity_status="resolved",
    )

    source = Source(
        url="https://example.com/statement-test",
        title="Statement Test Source",
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

    evidence = Evidence(
        person_id=person.id,
        source_id=source.id,
        evidence_type="source_passage",
        verification_status="unverified",
        extracted_text=(
            "The subject publicly stated that the organization "
            "should expand its research program."
        ),
        confidence=1.0,
        extraction_method="captured_source_segmentation",
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return person, source, evidence


def test_create_statement():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    service = StatementExtractionService()

    statement_date = datetime(2026, 1, 15)

    statement = service.create_statement(
        db=db,
        person=person,
        source=source,
        evidence=evidence,
        text=(
            "We should expand the organization's "
            "research program."
        ),
        statement_type="interview_statement",
        paraphrase="The speaker supported expanding the research program.",
        topic="research",
        context="Interview about organizational priorities.",
        statement_date=statement_date,
        attribution_status="direct_attribution",
        confidence=0.95,
    )

    assert statement.id is not None
    assert statement.person_id == person.id
    assert statement.source_id == source.id
    assert statement.evidence_id == evidence.id
    assert statement.statement_type == "interview_statement"
    assert statement.text == (
        "We should expand the organization's research program."
    )
    assert statement.paraphrase == (
        "The speaker supported expanding the research program."
    )
    assert statement.topic == "research"
    assert statement.context == (
        "Interview about organizational priorities."
    )
    assert statement.statement_date == statement_date
    assert statement.attribution_status == "direct_attribution"
    assert statement.confidence == 0.95

    db.close()
    engine.dispose()


def test_statement_text_is_normalized():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    service = StatementExtractionService()

    statement = service.create_statement(
        db=db,
        person=person,
        source=source,
        evidence=evidence,
        text="  We   support   this   proposal.  ",
    )

    assert statement.text == "We support this proposal."

    db.close()
    engine.dispose()


def test_confidence_is_clamped():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    service = StatementExtractionService()

    high = service.create_statement(
        db=db,
        person=person,
        source=source,
        evidence=evidence,
        text="High confidence statement.",
        confidence=5.0,
    )

    low = service.create_statement(
        db=db,
        person=person,
        source=source,
        evidence=evidence,
        text="Low confidence statement.",
        confidence=-5.0,
    )

    assert high.confidence == 1.0
    assert low.confidence == 0.0

    db.close()
    engine.dispose()


def test_duplicate_statement_is_not_created():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    service = StatementExtractionService()

    first = service.create_if_new(
        db=db,
        person=person,
        source=source,
        evidence=evidence,
        text="We support this proposal.",
    )

    second = service.create_if_new(
        db=db,
        person=person,
        source=source,
        evidence=evidence,
        text="  We   support   this   proposal. ",
    )

    assert first.id == second.id
    assert db.query(Statement).count() == 1

    db.close()
    engine.dispose()


def test_evidence_must_belong_to_person():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    other_person = Person(
        canonical_name="Other Statement Person",
        primary_profession="test",
        identity_confidence=1.0,
        identity_status="resolved",
    )

    db.add(other_person)
    db.commit()
    db.refresh(other_person)

    service = StatementExtractionService()

    with pytest.raises(
        ValueError,
        match="Evidence does not belong to the supplied Person",
    ):
        service.create_statement(
            db=db,
            person=other_person,
            source=source,
            evidence=evidence,
            text="Invalid attribution.",
        )

    db.close()
    engine.dispose()


def test_evidence_must_belong_to_source():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    other_source = Source(
        url="https://example.com/other-statement-source",
        title="Other Statement Source",
        publisher="Example",
        source_type="general_web",
        source_tier=4,
        reliability_score=0.5,
        is_verified=False,
    )

    db.add(other_source)
    db.commit()
    db.refresh(other_source)

    service = StatementExtractionService()

    with pytest.raises(
        ValueError,
        match="Evidence does not belong to the supplied Source",
    ):
        service.create_statement(
            db=db,
            person=person,
            source=other_source,
            evidence=evidence,
            text="Invalid source relationship.",
        )

    db.close()
    engine.dispose()


def test_empty_statement_is_rejected():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    service = StatementExtractionService()

    with pytest.raises(
        ValueError,
        match="Statement text cannot be empty",
    ):
        service.create_statement(
            db=db,
            person=person,
            source=source,
            evidence=evidence,
            text="   ",
        )

    db.close()
    engine.dispose()