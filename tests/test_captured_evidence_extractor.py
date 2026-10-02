from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import pytest

from backend.app.models import (
    Base,
    Person,
    Source,
    SourceCapture,
)
from backend.app.services.captured_evidence_extractor import (
    CapturedEvidenceExtractor,
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
        canonical_name="PERSONA-X Captured Evidence Test",
        primary_profession="test",
        identity_confidence=1.0,
        identity_status="resolved",
    )

    source = Source(
        url="https://example.com/captured-evidence-test",
        title="Captured Evidence Test",
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

    capture = SourceCapture(
        source_id=source.id,
        capture_version=1,
        http_status=200,
        content_type="text/html",
        content_hash="test-hash",
        extracted_text=(
            "PERSONA-X documented evidence passage containing "
            "enough information to qualify as evidence.\n"
            "This is a second independent source passage that "
            "also contains meaningful documented information.\n"
            "Too short."
        ),
        capture_status="captured",
    )

    db.add(capture)
    db.commit()
    db.refresh(capture)

    return person, source, capture


def test_split_passages_filters_short_text():
    engine = create_test_db()
    db = Session(engine)

    extractor = CapturedEvidenceExtractor()

    passages = extractor.split_passages(
        "This is a sufficiently long evidence passage "
        "that should be retained.\n"
        "Short."
    )

    assert len(passages) == 1
    assert passages[0].startswith("This is a sufficiently long")

    db.close()
    engine.dispose()


def test_extracts_source_grounded_evidence():
    engine = create_test_db()
    db = Session(engine)

    person, source, capture = create_entities(db)

    extractor = CapturedEvidenceExtractor()

    evidence = extractor.extract(
        db=db,
        person=person,
        source=source,
        capture=capture,
    )

    assert len(evidence) == 2

    assert evidence[0].person_id == person.id
    assert evidence[0].source_id == source.id

    assert evidence[0].evidence_type == "source_passage"
    assert evidence[0].verification_status == "unverified"
    assert evidence[0].confidence == 1.0

    assert evidence[0].extraction_method == (
        "captured_source_segmentation"
    )

    assert evidence[0].extraction_model is None

    assert evidence[0].source_locator == (
        f"capture:{capture.id};paragraph:1"
    )

    assert evidence[1].source_locator == (
        f"capture:{capture.id};paragraph:2"
    )

    assert "PERSONA-X documented evidence passage" in (
        evidence[0].extracted_text
    )

    db.close()
    engine.dispose()


def test_repeated_extraction_does_not_duplicate_evidence():
    engine = create_test_db()
    db = Session(engine)

    person, source, capture = create_entities(db)

    extractor = CapturedEvidenceExtractor()

    first = extractor.extract(
        db=db,
        person=person,
        source=source,
        capture=capture,
    )

    second = extractor.extract(
        db=db,
        person=person,
        source=source,
        capture=capture,
    )

    assert len(first) == 2
    assert len(second) == 2

    assert first[0].id == second[0].id
    assert first[1].id == second[1].id

    db.close()
    engine.dispose()


def test_capture_must_belong_to_source():
    engine = create_test_db()
    db = Session(engine)

    person, source, capture = create_entities(db)

    other_source = Source(
        url="https://example.com/other-source",
        title="Other Source",
        publisher="Example",
        source_type="general_web",
        source_tier=4,
        reliability_score=0.5,
        is_verified=False,
    )

    db.add(other_source)
    db.commit()
    db.refresh(other_source)

    extractor = CapturedEvidenceExtractor()

    with pytest.raises(
        ValueError,
        match="does not belong to the supplied Source",
    ):
        extractor.extract(
            db=db,
            person=person,
            source=other_source,
            capture=capture,
        )

    db.close()
    engine.dispose()


def test_failed_capture_cannot_become_evidence():
    engine = create_test_db()
    db = Session(engine)

    person, source, capture = create_entities(db)

    capture.capture_status = "failed"
    db.commit()

    extractor = CapturedEvidenceExtractor()

    with pytest.raises(
        ValueError,
        match="Only successfully captured sources",
    ):
        extractor.extract(
            db=db,
            person=person,
            source=source,
            capture=capture,
        )

    db.close()
    engine.dispose()