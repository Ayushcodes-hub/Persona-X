from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from backend.app.models.person import Person
from backend.app.models.research_job import ResearchJob


class ResearchAPIService:
    """
    Database-facing service used by the REST API.

    This layer deliberately does not duplicate the research engines.
    It manages API-level person/job lifecycle state.
    """

    @staticmethod
    def get_or_create_person(
        db: Session,
        person_name: str,
    ) -> Person:

        normalized_name = person_name.strip()

        person = (
            db.query(Person)
            .filter(Person.canonical_name == normalized_name)
            .first()
        )

        if person is not None:
            return person

        person = Person(
            canonical_name=normalized_name,
            identity_status="unresolved",
            identity_confidence=0.0,
        )

        db.add(person)
        db.flush()

        return person

    @staticmethod
    def create_research_job(
        db: Session,
        person_name: str,
        requested_scope: Optional[Dict[str, Any]] = None,
    ) -> ResearchJob:

        person = ResearchAPIService.get_or_create_person(
            db=db,
            person_name=person_name,
        )

        job = ResearchJob(
            person_id=person.id,
            job_type="full_research",
            status="queued",
            requested_scope=requested_scope,
            query_count=0,
            source_count=0,
            evidence_count=0,
            current_stage="queued",
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    @staticmethod
    def get_job(
        db: Session,
        job_id: int,
    ) -> Optional[ResearchJob]:

        return (
            db.query(ResearchJob)
            .filter(ResearchJob.id == job_id)
            .first()
        )

    @staticmethod
    def get_person_for_job(
        db: Session,
        job: ResearchJob,
    ) -> Optional[Person]:

        return (
            db.query(Person)
            .filter(Person.id == job.person_id)
            .first()
        )