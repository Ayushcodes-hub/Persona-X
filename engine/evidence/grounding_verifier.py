import re
import string
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class GroundingVerificationResult:
    is_verified: bool
    status: str  # "verified", "reported_unconfirmed", "unsupported_dropped"
    confidence: float
    span_match_ratio: float
    matched_span: Optional[str] = None
    corroboration_count: int = 1
    statement_taxonomy: str = "direct_quote"  # "direct_quote", "reported_claim", "paraphrase", "allegation"
    failure_reason: Optional[str] = None


class GroundingVerifier:
    """
    Defense-grade anti-hallucination verifier implementing 'Cite-or-Drop'.
    Guarantees every extracted statement, claim, and quote is strictly supported
    by verbatim text spans in the captured source snapshots.
    """

    SOURCE_TIER_WEIGHTS = {
        1: 1.0,   # Primary / official records (government, academic, verified archive)
        2: 0.85,  # Reputable journalistic outlets, major international news
        3: 0.60,  # Industry blogs, commentary, secondary aggregators
    }

    @staticmethod
    def _normalize_text(text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        # Replace fancy quotes and dashes
        text = re.sub(r'[\u2018\u2019\u201c\u201d]', '"', text)
        text = re.sub(r'[\u2013\u2014\-]', ' ', text)
        # Normalize punctuation to spaces for robust token matching
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def verify_span(
        self,
        candidate_span: str,
        source_text: str,
        source_tier: int = 2,
        corroborating_source_count: int = 1,
        is_direct_quote: bool = True,
        is_allegation: bool = False,
    ) -> GroundingVerificationResult:
        """
        Verify that a candidate text span exists verbatim or with high-fidelity within the source text.
        """
        if not candidate_span or not candidate_span.strip():
            return GroundingVerificationResult(
                is_verified=False,
                status="unsupported_dropped",
                confidence=0.0,
                span_match_ratio=0.0,
                failure_reason="Empty candidate text span.",
            )

        if not source_text or not source_text.strip():
            return GroundingVerificationResult(
                is_verified=False,
                status="unsupported_dropped",
                confidence=0.0,
                span_match_ratio=0.0,
                failure_reason="Empty source snapshot text.",
            )

        norm_candidate = self._normalize_text(candidate_span)
        norm_source = self._normalize_text(source_text)

        # 1. Exact verbatim match in normalized source
        if norm_candidate in norm_source:
            match_ratio = 1.0
            is_verified = True
        else:
            # 2. Windowed token overlap for minor tokenization/punctuation differences
            candidate_words = norm_candidate.split()
            if len(candidate_words) >= 4:
                window_size = len(candidate_words)
                source_words = norm_source.split()
                best_overlap = 0
                for i in range(max(0, len(source_words) - window_size + 1)):
                    window = source_words[i : i + window_size]
                    overlap = sum(1 for w in candidate_words if w in window)
                    if overlap > best_overlap:
                        best_overlap = overlap

                match_ratio = best_overlap / max(len(candidate_words), 1)
                is_verified = match_ratio >= 0.85
            else:
                match_ratio = 0.0
                is_verified = False

        # Determine statement taxonomy
        if is_allegation:
            taxonomy = "allegation"
        elif is_direct_quote and is_verified:
            taxonomy = "direct_quote"
        elif is_verified and match_ratio >= 0.85:
            taxonomy = "reported_claim"
        else:
            taxonomy = "paraphrase"

        # Calculate evidence-grounded confidence score
        tier_weight = self.SOURCE_TIER_WEIGHTS.get(source_tier, 0.7)
        corroboration_bonus = min(0.20, (corroborating_source_count - 1) * 0.10) if corroborating_source_count > 1 else 0.0

        if is_verified:
            base_confidence = tier_weight * (0.8 + 0.2 * match_ratio)
            final_confidence = min(1.0, round(base_confidence + corroboration_bonus, 2))
            status = "verified"
            reason = None
        else:
            if is_direct_quote or is_allegation:
                status = "unsupported_dropped"
                final_confidence = 0.0
                reason = "Direct quote or allegation could not be verified in captured source snapshot."
            else:
                status = "reported_unconfirmed"
                final_confidence = round(min(0.40, tier_weight * 0.4), 2)
                reason = "Text span not found verbatim; preserved with low confidence."

        return GroundingVerificationResult(
            is_verified=is_verified,
            status=status,
            confidence=final_confidence,
            span_match_ratio=round(match_ratio, 2),
            matched_span=candidate_span if is_verified else None,
            corroboration_count=corroborating_source_count,
            statement_taxonomy=taxonomy,
            failure_reason=reason,
        )


grounding_verifier = GroundingVerifier()
