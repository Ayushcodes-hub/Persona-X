from typing import Dict, List


UNIVERSAL_TOPIC_TAXONOMY: Dict[str, List[str]] = {
    "identity": [
        "personal_background",
        "nationality",
        "family",
        "early_life",
    ],
    "education": [
        "schooling",
        "university",
        "training",
        "academic_background",
    ],
    "career": [
        "career",
        "employment",
        "leadership",
        "professional_development",
    ],
    "business": [
        "company",
        "entrepreneurship",
        "investment",
        "funding",
        "products",
        "acquisitions",
    ],
    "science": [
        "research",
        "discovery",
        "technology",
        "innovation",
        "scientific_policy",
    ],
    "sports": [
        "competition",
        "performance",
        "training",
        "injury",
        "team",
        "sport_development",
    ],
    "arts": [
        "film",
        "television",
        "music",
        "literature",
        "visual_art",
        "performance",
        "production",
    ],
    "media": [
        "journalism",
        "broadcasting",
        "publishing",
        "media_industry",
    ],
    "public_activity": [
        "philanthropy",
        "charity",
        "foundation",
        "social_cause",
        "public_campaign",
    ],
    "public_policy": [
        "healthcare",
        "education_policy",
        "taxation",
        "economy",
        "employment",
        "immigration",
        "foreign_policy",
        "defense",
        "environment",
        "energy",
        "housing",
        "infrastructure",
        "technology_policy",
        "science_policy",
        "criminal_justice",
        "civil_rights",
        "social_policy",
        "trade",
        "government",
    ],
    "political_activity": [
        "election",
        "campaign",
        "party",
        "legislation",
        "government_office",
        "endorsement",
        "political_organization",
    ],
    "disputed_matters": [
        "controversy",
        "allegation",
        "legal_dispute",
        "investigation",
        "criticism",
    ],
}


def all_topic_categories() -> List[str]:
    return list(UNIVERSAL_TOPIC_TAXONOMY.keys())


def all_topics() -> List[str]:
    topics: List[str] = []

    for category_topics in UNIVERSAL_TOPIC_TAXONOMY.values():
        topics.extend(category_topics)

    return topics