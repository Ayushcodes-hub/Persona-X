from typing import Optional, Tuple


class TemporalClassifier:
    """
    Classifies the relationship between two dated observations.

    The classifier is deliberately conservative.

    It distinguishes:
        stable
        changed
        appeared
        disappeared
        insufficient_evidence

    It does not determine why a change occurred.
    """

    SUPPORTIVE = {
        "supportive",
        "support",
        "favor",
        "favorable",
    }

    OPPOSED = {
        "opposed",
        "oppose",
        "against",
    }

    BELIEF = {
        "belief_expressed",
        "believe",
    }

    def normalize_position(
        self,
        position: Optional[str],
    ) -> Optional[str]:
        if position is None:
            return None

        normalized = " ".join(position.lower().split())

        if normalized in self.SUPPORTIVE:
            return "supportive"

        if normalized in self.OPPOSED:
            return "opposed"

        if normalized in self.BELIEF:
            return "belief_expressed"

        return normalized

    def classify(
        self,
        earlier_position: Optional[str],
        later_position: Optional[str],
    ) -> Tuple[str, float, str]:
        """
        Return:

            change_type
            confidence
            explanation
        """

        earlier = self.normalize_position(
            earlier_position
        )
        later = self.normalize_position(
            later_position
        )

        if earlier is None or later is None:
            return (
                "insufficient_evidence",
                0.40,
                "One or both observations lack a documented position.",
            )

        if earlier == later:
            return (
                "stable",
                0.95,
                "The documented position is unchanged across the two observations.",
            )

        if (
            earlier == "supportive"
            and later == "opposed"
        ):
            return (
                "changed",
                0.90,
                "The later documented position differs from the earlier position.",
            )

        if (
            earlier == "opposed"
            and later == "supportive"
        ):
            return (
                "changed",
                0.90,
                "The later documented position differs from the earlier position.",
            )

        return (
            "changed",
            0.75,
            "The later documented position differs from the earlier position.",
        )