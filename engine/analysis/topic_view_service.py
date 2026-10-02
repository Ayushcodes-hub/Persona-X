from typing import Optional

from engine.analysis.topic_extractor import TopicExtractor
from engine.analysis.topic_schemas import TopicExtractionResult
from engine.analysis.view_extractor import ViewExtractor


class TopicViewExtractionService:
    """
    Coordinates topic extraction and conservative view extraction.

    Flow:

        source text
            ↓
        topic extraction
            ↓
        view extraction
            ↓
        structured TopicExtractionResult
    """

    def __init__(
        self,
        topic_extractor: Optional[TopicExtractor] = None,
        view_extractor: Optional[ViewExtractor] = None,
    ) -> None:
        self.topic_extractor = (
            topic_extractor or TopicExtractor()
        )
        self.view_extractor = (
            view_extractor or ViewExtractor()
        )

    def extract(
        self,
        text: str,
        context: str = "public_material",
        attribution_status: str = "unverified",
    ) -> TopicExtractionResult:
        result = self.topic_extractor.extract(
            text=text,
            context=context,
        )

        for topic in result.topics:
            views = self.view_extractor.extract(
                text=topic.source_text or "",
                topic=topic.topic,
                context=context,
                attribution_status=attribution_status,
            )

            result.views.extend(views)

        return result