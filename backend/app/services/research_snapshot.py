import hashlib

from backend.app.models.research_snapshot import ResearchSnapshot


class ResearchSnapshotService:
    """Persist an immutable fingerprinted snapshot of a research response."""

    def hash_response(self, response_text: str) -> str:
        return hashlib.sha256(response_text.encode('utf-8')).hexdigest()

    def create(
        self,
        db,
        research_query_id: int,
        response_text: str,
        provider: str,
        model_name: str,
        retrieval_method: str = 'browser_search',
    ) -> ResearchSnapshot:
        snapshot = ResearchSnapshot(
            research_query_id=research_query_id,
            provider=provider,
            model_name=model_name,
            retrieval_method=retrieval_method,
            raw_response=response_text,
            response_hash=self.hash_response(response_text),
            status='captured',
        )

        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return snapshot
