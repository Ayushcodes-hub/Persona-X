import re
from typing import Dict, List, Tuple

from engine.analysis.topic_schemas import TopicExtractionResult, TopicMention
from engine.analysis.topic_taxonomy import UNIVERSAL_TOPIC_TAXONOMY


class TopicExtractor:
    """
    Deterministic topic extraction foundation.

    This layer identifies topics from explicit lexical signals.
    It does not infer ideology, motives, personality, or political
    orientation.

    Later versions can add model-assisted extraction while retaining
    this deterministic layer as a transparent baseline.
    """

    TOPIC_KEYWORDS: Dict[str, List[str]] = {
        "healthcare": [
            "healthcare",
            "health care",
            "hospital",
            "medicine",
            "medical",
            "insurance",
            "medicare",
            "medicaid",
        ],
        "education_policy": [
            "education",
            "school",
            "schools",
            "university",
            "college",
            "student",
            "students",
            "teacher",
            "teachers",
        ],
        "taxation": [
            "tax",
            "taxes",
            "taxation",
            "tax rate",
            "tax policy",
        ],
        "economy": [
            "economy",
            "economic",
            "inflation",
            "growth",
            "gdp",
            "recession",
            "productivity",
        ],
        "employment": [
            "employment",
            "jobs",
            "job",
            "wages",
            "workers",
            "worker",
            "labor",
            "labour",
            "unemployment",
        ],
        "immigration": [
            "immigration",
            "immigrant",
            "immigrants",
            "migration",
            "migrant",
            "visa",
            "border",
            "citizenship",
        ],
        "foreign_policy": [
            "foreign policy",
            "diplomacy",
            "diplomatic",
            "international relations",
            "treaty",
            "alliance",
            "sanctions",
        ],
        "defense": [
            "defense",
            "defence",
            "military",
            "army",
            "navy",
            "air force",
            "armed forces",
        ],
        "environment": [
            "environment",
            "environmental",
            "climate",
            "pollution",
            "conservation",
            "emissions",
        ],
        "energy": [
            "energy",
            "electricity",
            "solar",
            "wind power",
            "renewable energy",
            "oil",
            "gas",
            "nuclear power",
        ],
        "housing": [
            "housing",
            "house prices",
            "rent",
            "rents",
            "mortgage",
            "affordable housing",
        ],
        "infrastructure": [
            "infrastructure",
            "roads",
            "rail",
            "railway",
            "transit",
            "transportation",
            "airport",
            "bridge",
        ],
        "technology_policy": [
            "artificial intelligence",
            "ai policy",
            "technology policy",
            "data privacy",
            "cybersecurity",
            "digital policy",
            "internet regulation",
        ],
        "science_policy": [
            "science policy",
            "research funding",
            "scientific research",
            "science funding",
        ],
        "criminal_justice": [
            "criminal justice",
            "crime",
            "policing",
            "police",
            "prison",
            "prisons",
            "incarceration",
        ],
        "civil_rights": [
            "civil rights",
            "equal rights",
            "discrimination",
            "racial equality",
            "voting rights",
        ],
        "social_policy": [
            "social policy",
            "welfare",
            "social security",
            "benefits",
            "poverty",
            "social programs",
        ],
        "trade": [
            "trade",
            "tariff",
            "tariffs",
            "imports",
            "exports",
            "free trade",
        ],
        "government": [
            "government",
            "administration",
            "public administration",
            "governance",
            "government reform",
        ],
        "research": [
            "research",
            "study",
            "studies",
            "experiment",
            "laboratory",
            "lab",
        ],
        "technology": [
            "technology",
            "software",
            "computer",
            "computing",
            "artificial intelligence",
            "machine learning",
            "robotics",
        ],
        "innovation": [
            "innovation",
            "innovative",
            "invention",
            "invented",
            "breakthrough",
        ],
        "competition": [
            "match",
            "matches",
            "competition",
            "tournament",
            "championship",
            "championships",
            "game",
        ],
        "training": [
            "training",
            "practice",
            "fitness",
            "workout",
            "preparation",
        ],
        "injury": [
            "injury",
            "injured",
            "rehabilitation",
            "recovery",
        ],
        "team": [
            "team",
            "club",
            "squad",
            "teammate",
            "teammates",
        ],
        "sport_development": [
            "grassroots sport",
            "youth sport",
            "sports development",
            "cricket development",
            "athlete development",
        ],
        "film": [
            "film",
            "films",
            "movie",
            "movies",
            "cinema",
            "filmmaking",
        ],
        "television": [
            "television",
            "tv series",
            "series",
            "television show",
        ],
        "music": [
            "music",
            "song",
            "songs",
            "album",
            "concert",
        ],
        "literature": [
            "book",
            "books",
            "novel",
            "novels",
            "literature",
            "writing",
        ],
        "visual_art": [
            "painting",
            "paintings",
            "sculpture",
            "artwork",
            "artworks",
            "gallery",
            "museum",
        ],
        "production": [
            "production",
            "producer",
            "produced",
            "production company",
        ],
        "journalism": [
            "journalism",
            "journalist",
            "reporting",
            "reporter",
            "investigation",
        ],
        "broadcasting": [
            "broadcast",
            "broadcasting",
            "television",
            "radio",
        ],
        "publishing": [
            "publisher",
            "publishing",
            "publication",
            "published",
        ],
        "philanthropy": [
            "philanthropy",
            "philanthropic",
            "donation",
            "donations",
            "donated",
            "charity",
            "charitable",
        ],
        "charity": [
            "charity",
            "charitable",
            "donation",
            "donated",
        ],
        "foundation": [
            "foundation",
            "nonprofit",
            "non-profit",
            "ngo",
        ],
        "social_cause": [
            "social cause",
            "cause",
            "advocacy",
            "advocate",
            "awareness campaign",
        ],
        "public_campaign": [
            "campaign",
            "public campaign",
            "awareness campaign",
        ],
        "company": [
            "company",
            "companies",
            "business",
            "corporation",
            "startup",
        ],
        "entrepreneurship": [
            "entrepreneur",
            "entrepreneurship",
            "founded",
            "founder",
            "co-founder",
        ],
        "investment": [
            "investment",
            "invested",
            "investor",
            "investors",
        ],
        "funding": [
            "funding",
            "funded",
            "financing",
            "investment round",
        ],
        "products": [
            "product",
            "products",
            "launch",
            "launched",
        ],
        "acquisitions": [
            "acquisition",
            "acquired",
            "merger",
            "mergers",
        ],
        "election": [
            "election",
            "elections",
            "elected",
            "reelected",
            "re-election",
        ],
        "campaign": [
            "campaign",
            "campaigning",
            "candidate",
        ],
        "party": [
            "political party",
            "party",
            "coalition",
        ],
        "legislation": [
            "legislation",
            "bill",
            "bills",
            "law",
            "laws",
            "act of parliament",
        ],
        "government_office": [
            "minister",
            "president",
            "governor",
            "mayor",
            "senator",
            "member of parliament",
            "mp",
            "cabinet",
            "government office",
        ],
        "endorsement": [
            "endorsed",
            "endorsement",
            "endorsed by",
        ],
        "political_organization": [
            "political organization",
            "political organisation",
            "party organization",
            "campaign organization",
        ],
        "controversy": [
            "controversy",
            "controversial",
            "dispute",
            "criticism",
        ],
        "allegation": [
            "allegation",
            "alleged",
            "accused",
            "accusation",
        ],
        "legal_dispute": [
            "lawsuit",
            "litigation",
            "legal dispute",
            "court case",
            "court",
        ],
        "investigation": [
            "investigation",
            "investigated",
            "probe",
            "inquiry",
        ],
    }

    TOPIC_CATEGORY_MAP: Dict[str, str] = {}

    def __init__(self) -> None:
        self._build_category_map()

    def _build_category_map(self) -> None:
        category_map: Dict[str, str] = {}

        for category, topics in UNIVERSAL_TOPIC_TAXONOMY.items():
            for topic in topics:
                category_map[topic] = category

        self.TOPIC_CATEGORY_MAP = category_map

    @staticmethod
    def normalize_text(text: str) -> str:
        return " ".join(text.split()).strip()

    @staticmethod
    def _contains_keyword(text: str, keyword: str) -> bool:
        escaped = re.escape(keyword.lower())

        if " " in keyword:
            return re.search(escaped, text.lower()) is not None

        return re.search(
            rf"\b{escaped}\b",
            text.lower(),
        ) is not None

    def _find_matches(
        self,
        text: str,
    ) -> List[Tuple[str, str]]:
        normalized = self.normalize_text(text)
        matches: List[Tuple[str, str]] = []

        for topic, keywords in self.TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if self._contains_keyword(normalized, keyword):
                    matches.append((topic, keyword))
                    break

        return matches

    def _confidence(
        self,
        topic: str,
        matched_keyword: str,
    ) -> float:
        """
        Confidence here means confidence that the text contains
        a lexical signal for the topic.

        It does NOT mean that the underlying claim is true.
        """

        if topic in self.TOPIC_CATEGORY_MAP:
            return 0.90

        if matched_keyword:
            return 0.80

        return 0.70

    def extract(
        self,
        text: str,
        context: str = "public_material",
    ) -> TopicExtractionResult:
        normalized = self.normalize_text(text)

        if not normalized:
            return TopicExtractionResult()

        matches = self._find_matches(normalized)

        topics: List[TopicMention] = []

        seen = set()

        for topic, keyword in matches:
            if topic in seen:
                continue

            seen.add(topic)

            topics.append(
                TopicMention(
                    topic=topic,
                    context=context,
                    source_text=normalized,
                    confidence=self._confidence(
                        topic,
                        keyword,
                    ),
                    extraction_method="deterministic_keyword",
                    status="extracted",
                )
            )

        return TopicExtractionResult(topics=topics)