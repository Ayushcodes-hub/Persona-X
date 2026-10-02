from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import pytest

from backend.app.models import (
    Base,
    Claim,
    Evidence,
    Person,
    Source,
)
from backend.app.services.claim_extraction import (
    ClaimExtractionService,
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
        canonical_name="PERSONA-X Claim Test",
        primary_profession="test",
        identity_confidence=1.0,
        identity_status="resolved",
    )

    source = Source(
        url="https://example.com/claim-test",
        title="Claim Test Source",
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
            "The subject became chief executive officer "
            "of the organization in 2014."
        ),
        confidence=1.0,
        extraction_method="captured_source_segmentation",
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return person, source, evidence


def test_create_structured_claim():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    service = ClaimExtractionService()

    claim = service.create_claim(
        db=db,
        person=person,
        evidence=evidence,
        claim_type="career",
        claim_text=(
            "The subject became chief executive officer "
            "of the organization in 2014."
        ),
        subject="PERSONA-X Claim Test",
        predicate="became_ceo_of",
        object_value="Example Organization",
        topic="career",
        confidence=0.9,
    )

    assert claim.id is not None
    assert claim.person_id == person.id
    assert claim.evidence_id == evidence.id
    assert claim.claim_type == "career"
    assert claim.predicate == "became_ceo_of"
    assert claim.object_value == "Example Organization"
    assert claim.verification_status == "unverified"
    assert claim.confidence == 0.9

    db.close()
    engine.dispose()


def test_claim_text_is_normalized():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    service = ClaimExtractionService()

    claim = service.create_claim(
        db=db,
        person=person,
        evidence=evidence,
        claim_type=" career ",
        claim_text="  A   normalized   claim.  ",
    )

    assert claim.claim_type == "career"
    assert claim.claim_text == "A normalized claim."

    db.close()
    engine.dispose()


def test_confidence_is_clamped():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    service = ClaimExtractionService()

    high = service.create_claim(
        db=db,
        person=person,
        evidence=evidence,
        claim_type="test",
        claim_text="High confidence claim",
        confidence=5.0,
    )

    low = service.create_claim(
        db=db,
        person=person,
        evidence=evidence,
        claim_type="test",
        claim_text="Low confidence claim",
        confidence=-5.0,
    )

    assert high.confidence == 1.0
    assert low.confidence == 0.0

    db.close()
    engine.dispose()


def test_duplicate_claim_is_not_created():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    service = ClaimExtractionService()

    first = service.create_if_new(
        db=db,
        person=person,
        evidence=evidence,
        claim_type="career",
        claim_text="The subject became CEO.",
    )

    second = service.create_if_new(
        db=db,
        person=person,
        evidence=evidence,
        claim_type="career",
        claim_text="  The   subject became CEO. ",
    )

    assert first.id == second.id

    count = db.query(Claim).count()

    assert count == 1

    db.close()
    engine.dispose()


def test_evidence_must_belong_to_person():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    other_person = Person(
        canonical_name="Other Person",
        primary_profession="test",
        identity_confidence=1.0,
        identity_status="resolved",
    )

    db.add(other_person)
    db.commit()
    db.refresh(other_person)

    service = ClaimExtractionService()

    with pytest.raises(
        ValueError,
        match="Evidence does not belong to the supplied Person",
    ):
        service.create_claim(
            db=db,
            person=other_person,
            evidence=evidence,
            claim_type="test",
            claim_text="Invalid ownership claim",
        )

    db.close()
    engine.dispose()


def test_empty_claim_is_rejected():
    engine = create_test_db()
    db = Session(engine)

    person, source, evidence = create_entities(db)

    service = ClaimExtractionService()

    with pytest.raises(
        ValueError,
        match="Claim text cannot be empty",
    ):
        service.create_claim(
            db=db,
            person=person,
            evidence=evidence,
            claim_type="test",
            claim_text="   ",
        )

    db.close()
    engine.dispose()