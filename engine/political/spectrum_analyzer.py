from typing import Dict, List, Optional, Tuple

from engine.political.schemas import (
    PoliticalDimension,
    PoliticalEvidence,
    PoliticalPosition,
    PoliticalSpectrum,
    PoliticalSufficiency,
)


# Issue orientation mapping: (issue, position) -> (axis, left_right_value [-1.0 Left to +1.0 Right], indicator_text)
# Values: Negative = Left, Positive = Right
ISSUE_SPECTRUM_MAP: Dict[Tuple[str, str], Tuple[str, float, str]] = {
    # Economic Policy
    ("welfare", "support"): ("economic", -0.70, "Advocates social safety net and public welfare expansion"),
    ("welfare", "favor"): ("economic", -0.70, "Favors welfare support programs"),
    ("welfare", "oppose"): ("economic", 0.70, "Opposes expanded welfare entitlements"),
    ("welfare", "against"): ("economic", 0.70, "Stands against welfare entitlement growth"),
    ("taxation", "support"): ("economic", -0.60, "Supports progressive taxation / public revenue mobilization"),
    ("taxation", "favor"): ("economic", -0.60, "Favors tax-funded public investment"),
    ("taxation", "oppose"): ("economic", 0.65, "Opposes tax increases; supports fiscal conservatism"),
    ("taxation", "against"): ("economic", 0.65, "Advocates tax relief and private capital retention"),
    ("government_spending", "support"): ("economic", -0.65, "Supports public infrastructure and state spending"),
    ("government_spending", "oppose"): ("economic", 0.70, "Favors fiscal austerity and limited government spending"),
    ("business_regulation", "support"): ("economic", -0.60, "Advocates corporate regulation and market oversight"),
    ("business_regulation", "oppose"): ("economic", 0.70, "Advocates free-market deregulation and enterprise autonomy"),
    ("labor_policy", "support"): ("economic", -0.75, "Supports labor unions, collective bargaining, and workers' rights"),
    ("labor_policy", "oppose"): ("economic", 0.65, "Favors right-to-work and flexible labor markets"),
    ("deficit_and_debt", "oppose"): ("economic", 0.50, "Stresses deficit reduction and fiscal discipline"),

    # Social Policy
    ("civil_rights", "support"): ("social", -0.70, "Champions civil rights protections and social equality"),
    ("civil_rights", "favor"): ("social", -0.70, "Favors progressive equality legislation"),
    ("healthcare", "support"): ("social", -0.65, "Supports universal / state-guaranteed healthcare access"),
    ("healthcare", "oppose"): ("social", 0.55, "Prefers market-based private healthcare solutions"),
    ("education", "support"): ("social", -0.50, "Favors state-funded universal public education"),
    ("education", "oppose"): ("social", 0.50, "Favors school choice and private educational institutions"),
    ("social_programs", "support"): ("social", -0.70, "Promotes state-backed community and social assistance"),
    ("family_policy", "support"): ("social", 0.50, "Emphasizes traditional family structures and cultural heritage"),
    ("religious_freedom", "support"): ("social", 0.40, "Advocates traditional religious expression in public life"),
    ("criminal_justice", "support"): ("social", -0.60, "Favors criminal justice reform and restorative policies"),
    ("criminal_justice", "oppose"): ("social", 0.60, "Emphasizes strict law enforcement and mandatory sentencing"),

    # Environment & Energy
    ("climate_policy", "support"): ("social", -0.75, "Supports binding government climate action and emissions controls"),
    ("climate_policy", "oppose"): ("social", 0.65, "Prioritizes industrial competitiveness over climate regulations"),
    ("renewable_energy", "support"): ("economic", -0.50, "Favors clean-energy subsidies and green transition"),
    ("fossil_fuels", "support"): ("economic", 0.60, "Supports domestic oil, gas, and fossil fuel development"),
    ("environmental_regulation", "support"): ("economic", -0.65, "Backs environmental preservation rules on industry"),

    # Immigration
    ("border_policy", "support"): ("social", 0.65, "Supports strict border security and enforcement"),
    ("border_policy", "oppose"): ("social", -0.60, "Advocates liberalized border and humanitarian entry standards"),
    ("asylum", "support"): ("social", -0.70, "Champions humanitarian asylum protections"),
    ("citizenship", "support"): ("social", -0.55, "Supports pathways to legal citizenship for undocumented residents"),

    # Governance & Institutions
    ("democratic_institutions", "support"): ("governance", -0.40, "Promotes institutional democracy, voting rights, and transparency"),
    ("executive_power", "support"): ("governance", 0.50, "Favors strong executive authority and decisiveness"),
    ("rule_of_law", "support"): ("governance", 0.10, "Emphasizes constitutional legal order"),

    # Foreign Policy
    ("alliances", "support"): ("foreign_policy", -0.40, "Advocates multilateral alliances and international treaties"),
    ("defense", "support"): ("foreign_policy", 0.55, "Favors robust defense spending and military deterrence"),
    ("diplomacy", "support"): ("foreign_policy", -0.50, "Prioritizes diplomatic engagement over unilateral action"),
}


class PoliticalSpectrumAnalyzer:
    """
    Evidence-grounded political spectrum analyzer.
    Determines political placement along a calibrated Left (-1.0) to Right (+1.0) spectrum.
    """

    @staticmethod
    def _classify_spectrum_label(score: float, economic: float, social: float) -> str:
        # Check for cross-axis divergence (e.g. Libertarian / Fiscally Conservative Socially Liberal)
        if economic > 0.25 and social < -0.25:
            return "Fiscally Conservative / Socially Liberal (Libertarian-Leaning)"
        if economic < -0.25 and social > 0.25:
            return "Economically Progressive / Socially Conservative (Communitarian)"

        if score <= -0.60:
            return "Left-Wing (Democratic Socialist / Left)"
        elif -0.60 < score <= -0.20:
            return "Center-Left (Social Democratic / Progressive)"
        elif -0.20 < score <= 0.20:
            return "Centrist / Pragmatic (Balanced Multi-Perspective)"
        elif 0.20 < score <= 0.60:
            return "Center-Right (Liberal-Conservative / Market-Oriented)"
        else:
            return "Right-Wing (Traditionalist / Conservative)"

    def analyze(
        self,
        person_name: str,
        sufficiency: PoliticalSufficiency,
        dimensions: List[PoliticalDimension],
        political_activity: List[PoliticalEvidence],
    ) -> PoliticalSpectrum:
        """
        Synthesize documented evidence into a validated Left-to-Right political spectrum position.
        """
        if not sufficiency.sufficient or not dimensions:
            return PoliticalSpectrum(
                applicable=False,
                spectrum_score=None,
                spectrum_label="Insufficient Public Political Record",
                economic_axis=None,
                social_axis=None,
                governance_axis=None,
                foreign_policy_axis=None,
                rationale=(
                    f"Public records for {person_name} contain insufficient verified policy positions "
                    f"or political endorsements to determine a reliable left-to-right orientation. "
                    f"PERSONA-X does not infer political views from profession, nationality, or associations."
                ),
                confidence=sufficiency.confidence,
                key_indicators=[],
            )

        axis_scores: Dict[str, List[float]] = {
            "economic": [],
            "social": [],
            "governance": [],
            "foreign_policy": [],
        }
        indicators: List[str] = []

        for dim in dimensions:
            for pos in dim.positions:
                key = (pos.issue.lower(), pos.position.lower())
                if key in ISSUE_SPECTRUM_MAP:
                    axis, val, desc = ISSUE_SPECTRUM_MAP[key]
                    axis_scores[axis].append(val)
                    indicators.append(f"{desc} ({pos.issue}: {pos.position})")
                else:
                    # Generic heuristic fallback based on position
                    if pos.position in {"support", "favor"}:
                        if "economic" in dim.name.lower() or "welfare" in pos.issue:
                            axis_scores["economic"].append(-0.4)
                            indicators.append(f"Favors active policy on {pos.issue}")
                        else:
                            axis_scores["social"].append(-0.2)
                    elif pos.position in {"oppose", "against"}:
                        if "economic" in dim.name.lower():
                            axis_scores["economic"].append(0.4)
                            indicators.append(f"Opposes regulatory intervention on {pos.issue}")

        # Compute averages for each axis
        avg_economic = (
            sum(axis_scores["economic"]) / len(axis_scores["economic"])
            if axis_scores["economic"]
            else 0.0
        )
        avg_social = (
            sum(axis_scores["social"]) / len(axis_scores["social"])
            if axis_scores["social"]
            else 0.0
        )
        avg_governance = (
            sum(axis_scores["governance"]) / len(axis_scores["governance"])
            if axis_scores["governance"]
            else 0.0
        )
        avg_foreign = (
            sum(axis_scores["foreign_policy"]) / len(axis_scores["foreign_policy"])
            if axis_scores["foreign_policy"]
            else 0.0
        )

        # Weighted composite score: Economic (40%), Social (35%), Governance (15%), Foreign Policy (10%)
        active_weights = []
        weighted_sum = 0.0

        if axis_scores["economic"]:
            weighted_sum += avg_economic * 0.40
            active_weights.append(0.40)
        if axis_scores["social"]:
            weighted_sum += avg_social * 0.35
            active_weights.append(0.35)
        if axis_scores["governance"]:
            weighted_sum += avg_governance * 0.15
            active_weights.append(0.15)
        if axis_scores["foreign_policy"]:
            weighted_sum += avg_foreign * 0.10
            active_weights.append(0.10)

        if not active_weights:
            # If positions had no recognized orientation mappings
            return PoliticalSpectrum(
                applicable=True,
                spectrum_score=0.0,
                spectrum_label="Independent / Undefined Spectrum",
                economic_axis=0.0,
                social_axis=0.0,
                governance_axis=0.0,
                foreign_policy_axis=0.0,
                rationale=(
                    f"Documented political activity exists for {person_name}, but specific issue stances "
                    f"do not align cleanly with traditional left/right polarities."
                ),
                confidence=min(sufficiency.confidence, 0.5),
                key_indicators=["Non-traditional / cross-cutting political stances documented"],
            )

        total_weight = sum(active_weights)
        overall_score = round(max(-1.0, min(1.0, weighted_sum / total_weight)), 2)
        label = self._classify_spectrum_label(overall_score, avg_economic, avg_social)

        # Analytical rationale synthesis
        rationale_parts = [
            f"Based on {len(indicators)} documented policy positions in verified public records, "
            f"{person_name} is evaluated as **{label}** with a composite spectrum score of **{overall_score:+.2f}** "
            f"(scale: -1.00 full Left to +1.00 full Right)."
        ]
        if axis_scores["economic"]:
            econ_desc = "left-leaning (state/welfare emphasis)" if avg_economic < -0.1 else ("right-leaning (market/fiscal discipline)" if avg_economic > 0.1 else "centrist")
            rationale_parts.append(f"Economic axis is scored at **{avg_economic:+.2f}** ({econ_desc}).")
        if axis_scores["social"]:
            social_desc = "progressive (civil liberties/reform)" if avg_social < -0.1 else ("conservative (traditionalist/order)" if avg_social > 0.1 else "moderate")
            rationale_parts.append(f"Social axis is scored at **{avg_social:+.2f}** ({social_desc}).")

        rationale = " ".join(rationale_parts)

        return PoliticalSpectrum(
            applicable=True,
            spectrum_score=overall_score,
            spectrum_label=label,
            economic_axis=round(avg_economic, 2) if axis_scores["economic"] else None,
            social_axis=round(avg_social, 2) if axis_scores["social"] else None,
            governance_axis=round(avg_governance, 2) if axis_scores["governance"] else None,
            foreign_policy_axis=round(avg_foreign, 2) if axis_scores["foreign_policy"] else None,
            rationale=rationale,
            confidence=round(sufficiency.confidence, 2),
            key_indicators=indicators[:8],
        )
