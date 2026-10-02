from sqlalchemy.orm import Session

from backend.app.models.research_job import ResearchJob
from backend.app.repositories.research_repository import ResearchRepository
from backend.app.services.groq_service import GroqService
from backend.app.services.research_snapshot import ResearchSnapshotService
from engine.research.schemas import ResearchResponse


class BrowserResearchPipeline:
    """Execute browser research and persist its raw research snapshot."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.groq = GroqService()
        self.repository = ResearchRepository(db)
        self.snapshots = ResearchSnapshotService()

    def research(
        self,
        research_job: ResearchJob,
        query_text: str,
        profession_context: str | None = None,
        topic: str | None = None,
        max_completion_tokens: int = 4096,
    ) -> ResearchResponse:
        query = self.repository.create_query(
            research_job_id=research_job.id,
            query_text=query_text,
            query_type='browser_search',
            profession_context=profession_context,
            topic=topic,
        )

        try:
            response = self.groq.client.chat.completions.create(
                model=self.groq.model,
                messages=[
                    {
                        'role': 'system',
                        'content': (
                            'You are the PERSONA-X research engine. '
                            'Research only publicly available information. '
                            'Prefer primary and authoritative sources. '
                            'Do not invent facts or sources. '
                            'Distinguish documented facts from claims, allegations, '
                            'and inference.'
                        ),
                    },
                    {
                        'role': 'user',
                        'content': query_text,
                    },
                ],
                tools=[{'type': 'browser_search'}],
                tool_choice='required',
                temperature=0,
                max_completion_tokens=max_completion_tokens,
            )

            content = response.choices[0].message.content or ''

            self.snapshots.create(
                db=self.db,
                research_query_id=query.id,
                response_text=content,
                provider='groq',
                model_name=self.groq.model,
                retrieval_method='browser_search',
            )

            query.status = 'completed'
            query.result_count = 0
            self.db.commit()

            return ResearchResponse(
                query=query_text,
                results=[],
                search_status='completed',
                error=None if content else 'Browser search returned empty content.',
            )

        except Exception as exc:
            query.status = 'failed'
            query.execution_error = str(exc)
            self.db.commit()

            return ResearchResponse(
                query=query_text,
                results=[],
                search_status='error',
                error=str(exc),
            )
