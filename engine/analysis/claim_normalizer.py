import re
from typing import Optional


class ClaimNormalizer:
    """
    Conservative normalization for deterministic claim comparison.

    This component does not determine whether a claim is true.
    It only makes comparable textual fields easier to compare.
    """

    POLARITY_MAP = {
        "support": "supportive",
        "supportive": "supportive",
        "favor": "supportive",
        "favorable": "supportive",
        "oppose": "opposed",
        "opposed": "opposed",
        "against": "opposed",
        "reject": "opposed",
        "rejected": "opposed",
        "neutral": "neutral",
        "unknown": "unknown",
    }

    def normalize_text(
        self,
        value: Optional[str],
    ) -> Optional[str]:
        if value is None:
            return None

        normalized = value.lower().strip()

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        normalized = re.sub(
            r"[^\w\s.-]",
            "",
            normalized,
        )

        return normalized or None

    def normalize_topic(
        self,
        value: Optional[str],
    ) -> Optional[str]:
        return self.normalize_text(value)

    def normalize_subject(
        self,
        value: Optional[str],
    ) -> Optional[str]:
        return self.normalize_text(value)

    def normalize_predicate(
        self,
        value: Optional[str],
    ) -> Optional[str]:
        return self.normalize_text(value)

    def normalize_object(
        self,
        value: Optional[str],
    ) -> Optional[str]:
        return self.normalize_text(value)

    def normalize_polarity(
        self,
        value: Optional[str],
    ) -> Optional[str]:
        if value is None:
            return None

        normalized = self.normalize_text(value)

        if normalized is None:
            return None

        return self.POLARITY_MAP.get(
            normalized,
            normalized,
        )

    def normalize_claim(
        self,
        claim_text: str,
    ) -> str:
        return (
            self.normalize_text(claim_text)
            or ""
        )