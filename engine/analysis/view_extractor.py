import re
from typing import Dict, List, Optional, Tuple

from engine.analysis.topic_schemas import ViewMention


class ViewExtractor:
    """
    Deterministic extraction of explicitly expressed positions.

    This is intentionally conservative. It looks for linguistic
    indicators of a position rather than treating every topic mention
    as a view.

    It does not infer political ideology.
    """

    POSITION_PATTERNS: List[Tuple[str, str]] = [
        (
            "support",
            r"\b(?:i|we|he|she|they|the person)\s+"
            r"(?:strongly\s+)?support(?:s|ed)?\b",
        ),
        (
            "oppose",
            r"\b(?:i|we|he|she|they|the person)\s+"
            r"(?:strongly\s+)?oppose(?:s|d)?\b",
        ),
        (
            "favor",
            r"\b(?:i|we|he|she|they|the person)\s+"
            r"(?:strongly\s+)?favor(?:s|ed)?\b",
        ),
        (
            "against",
            r"\b(?:i|we|he|she|they|the person)\s+"
            r"(?:strongly\s+)?(?:am|are|is|was|were)\s+against\b",
        ),
        (
            "believe",
            r"\b(?:i|we|he|she|they)\s+believe(?:s|d)?\b",
        ),
        (
            "advocate",
            r"\b(?:i|we|he|she|they)\s+"
            r"advocate(?:s|d)?\s+for\b",
        ),
        (
            "call_for",
            r"\b(?:i|we|he|she|they)\s+"
            r"call(?:s|ed)?\s+for\b",
        ),
        (
            "oppose_policy",
            r"\b(?:i|we|he|she|they)\s+"
            r"(?:want|wants|wanted)\s+to\s+(?:end|stop|abolish|remove)\b",
        ),
        (
            "support_policy",
            r"\b(?:i|we|he|she|they)\s+"
            r"(?:want|wants|wanted)\s+to\s+(?:expand|increase|create|fund)\b",
        ),
    ]

    def normalize_text(self, text: str) -> str:
        return " ".join(text.split()).strip()

    def _detect_position_type(
        self,
        text: str,
    ) -> Optional[str]:
        normalized = text.lower()

        for position_type, pattern in self.POSITION_PATTERNS:
            if re.search(pattern, normalized):
                return position_type

        return None

    def _position_from_type(
        self,
        position_type: str,
    ) -> Optional[str]:
        support_types = {
            "support",
            "favor",
            "advocate",
            "call_for",
            "support_policy",
        }

        oppose_types = {
            "oppose",
            "against",
            "oppose_policy",
        }

        if position_type in support_types:
            return "supportive"

        if position_type in oppose_types:
            return "opposed"

        if position_type == "believe":
            return "belief_expressed"

        return None

    def extract(
        self,
        text: str,
        topic: Optional[str] = None,
        context: str = "public_statement",
        attribution_status: str = "unverified",
    ) -> List[ViewMention]:
        normalized = self.normalize_text(text)

        if not normalized:
            return []

        position_type = self._detect_position_type(normalized)

        if position_type is None:
            return []

        position = self._position_from_type(position_type)

        return [
            ViewMention(
                topic=topic or "unspecified",
                position=position,
                position_type=position_type,
                context=context,
                supporting_text=normalized,
                confidence=0.80,
                attribution_status=attribution_status,
                extraction_method="deterministic_position_pattern",
                status="extracted",
            )
        ]