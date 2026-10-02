from typing import List

from sqlalchemy.orm import Session

from backend.app.models.evidence import Evidence
from backend.app.models.person import Person
from backend.app.models.source import Source
from backend.app.models.source_capture import SourceCapture
from backend.app.services.evidence_extraction import EvidenceExtractionService


class CapturedEvidenceExtractor:
    """
    Extract source-grounded evidence passages from a captured source.

    This stage is deliberately deterministic:
    it never invents facts or claims that are not present
    in the captured source text.
    """

    MIN_PASSAGE_LENGTH = 40

    def __init__(self):
        self.evidence_service = EvidenceExtractionService()

    def normalize_passage(self, passage: str) -> str:
        return " ".join(passage.split()).strip()

    def split_passages(self, text: str) -> List[str]:
        if not text:
            return []

        normalized = text.replace("\r\n", "\n").replace("\r", "\n")

        passages = []

        for block in normalized.split("\n"):
            passage = self.normalize_passage(block)

            if len(passage) < self.MIN_PASSAGE_LENGTH:
                continue

            passages.append(passage)

        return passages

    def extract(
        self,
        db: Session,
        person: Person,
        source: Source,
        capture: SourceCapture,
        evidence_type: str = "source_passage",
    ) -> List[Evidence]:

        if capture.source_id != source.id:
            raise ValueError(
                "SourceCapture does not belong to the supplied Source."
            )

        if capture.capture_status != "captured":
            raise ValueError(
                "Only successfully captured sources can be "
                "converted into evidence."
            )

        passages = self.split_passages(
            capture.extracted_text or ""
        )

        evidence_records: List[Evidence] = []

        for index, passage in enumerate(passages, start=1):
            evidence = self.evidence_service.create_if_new(
                db=db,
                person=person,
                source=source,
                extracted_text=passage,
                evidence_type=evidence_type,
                source_locator=(
                    f"capture:{capture.id};paragraph:{index}"
                ),
                confidence=1.0,
                extraction_method="captured_source_segmentation",
                extraction_model=None,
                verification_status="unverified",
            )

            evidence_records.append(evidence)

        return evidence_records