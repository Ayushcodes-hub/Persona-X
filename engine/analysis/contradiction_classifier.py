from typing import Optional, Tuple

from engine.analysis.claim_normalizer import (
    ClaimNormalizer,
)
from engine.analysis.contradiction_schemas import (
    ClaimObservation,
)


class ContradictionClassifier:
    """
    Conservative deterministic classifier.

    A potential inconsistency requires:

        1. matching topic when topic information exists
        2. matching subject when subject information exists
        3. comparable propositions
        4. opposing polarity

    Missing information lowers the classification to
    insufficient_evidence rather than producing a false contradiction.
    """

    def __init__(
        self,
        normalizer: Optional[ClaimNormalizer] = None,
    ):
        self.normalizer = (
            normalizer or ClaimNormalizer()
        )

    def _field_match(
        self,
        first: Optional[str],
        second: Optional[str],
    ) -> Optional[bool]:
        """
        Return:

            True  -> explicitly matching
            False -> explicitly different
            None  -> insufficient information
        """

        first_normalized = (
            self.normalizer.normalize_text(first)
        )
        second_normalized = (
            self.normalizer.normalize_text(second)
        )

        if (
            first_normalized is None
            or second_normalized is None
        ):
            return None

        return first_normalized == second_normalized

    def topic_match(
        self,
        first: ClaimObservation,
        second: ClaimObservation,
    ) -> Optional[bool]:
        return self._field_match(
            first.topic,
            second.topic,
        )

    def subject_match(
        self,
        first: ClaimObservation,
        second: ClaimObservation,
    ) -> Optional[bool]:
        return self._field_match(
            first.subject,
            second.subject,
        )

    def proposition_match(
        self,
        first: ClaimObservation,
        second: ClaimObservation,
    ) -> Optional[bool]:
        """
        Compare predicate/object when both are available.

        If structured proposition fields are unavailable, the classifier
        does not invent a proposition match from free text alone.
        """

        predicates_available = (
            first.predicate is not None
            and second.predicate is not None
        )

        objects_available = (
            first.object_value is not None
            and second.object_value is not None
        )

        if not predicates_available:
            return None

        predicate_match = (
            self._field_match(
                first.predicate,
                second.predicate,
            )
        )

        if predicate_match is False:
            return False

        if objects_available:
            object_match = self._field_match(
                first.object_value,
                second.object_value,
            )

            if object_match is False:
                return False

            if object_match is None:
                return None

        return predicate_match

    def polarity_conflict(
        self,
        first: ClaimObservation,
        second: ClaimObservation,
    ) -> Optional[bool]:
        first_polarity = (
            self.normalizer.normalize_polarity(
                first.polarity
            )
        )

        second_polarity = (
            self.normalizer.normalize_polarity(
                second.polarity
            )
        )

        if (
            first_polarity is None
            or second_polarity is None
        ):
            return None

        if (
            first_polarity == "supportive"
            and second_polarity == "opposed"
        ):
            return True

        if (
            first_polarity == "opposed"
            and second_polarity == "supportive"
        ):
            return True

        return False

    def classify(
        self,
        first: ClaimObservation,
        second: ClaimObservation,
    ) -> Tuple[
        str,
        float,
        str,
        bool,
        bool,
        bool,
        bool,
    ]:
        topic_match_value = self.topic_match(
            first,
            second,
        )

        subject_match_value = self.subject_match(
            first,
            second,
        )

        proposition_match_value = (
            self.proposition_match(
                first,
                second,
            )
        )

        polarity_conflict_value = (
            self.polarity_conflict(
                first,
                second,
            )
        )

        topic_matches = (
            topic_match_value is True
            or topic_match_value is None
        )

        subject_matches = (
            subject_match_value is True
            or subject_match_value is None
        )

        proposition_matches = (
            proposition_match_value is True
        )

        polarity_conflicts = (
            polarity_conflict_value is True
        )

        if (
            polarity_conflicts
            and topic_matches
            and subject_matches
            and proposition_matches
        ):
            return (
                "potential_inconsistency",
                0.90,
                (
                    "The documented claims concern the same "
                    "structured proposition but express opposing "
                    "positions."
                ),
                topic_match_value is True,
                subject_match_value is True,
                proposition_match_value is True,
                True,
            )

        if (
            topic_match_value is False
            or subject_match_value is False
            or proposition_match_value is False
        ):
            return (
                "compatible",
                0.85,
                (
                    "The available structured evidence does not "
                    "establish the same proposition."
                ),
                topic_match_value is True,
                subject_match_value is True,
                proposition_match_value is True,
                False,
            )

        return (
            "insufficient_evidence",
            0.40,
            (
                "The available structured fields are insufficient "
                "to establish whether the claims conflict."
            ),
            topic_match_value is True,
            subject_match_value is True,
            proposition_match_value is True,
            polarity_conflicts,
        )