POLITICAL_DIMENSIONS = {
    "economic_policy": {
        "name": "Economic Policy",
        "issues": [
            "taxation",
            "government_spending",
            "deficit_and_debt",
            "labor_policy",
            "trade",
            "business_regulation",
            "welfare",
        ],
    },
    "social_policy": {
        "name": "Social Policy",
        "issues": [
            "education",
            "healthcare",
            "civil_rights",
            "religious_freedom",
            "family_policy",
            "criminal_justice",
            "social_programs",
        ],
    },
    "government_and_institutions": {
        "name": "Government and Institutions",
        "issues": [
            "democratic_institutions",
            "rule_of_law",
            "executive_power",
            "judicial_independence",
            "elections",
            "corruption_and_transparency",
        ],
    },
    "foreign_policy": {
        "name": "Foreign Policy",
        "issues": [
            "alliances",
            "war_and_peace",
            "defense",
            "international_trade",
            "international_organizations",
            "diplomacy",
        ],
    },
    "immigration": {
        "name": "Immigration",
        "issues": [
            "border_policy",
            "legal_immigration",
            "asylum",
            "citizenship",
            "refugee_policy",
        ],
    },
    "environment_and_energy": {
        "name": "Environment and Energy",
        "issues": [
            "climate_policy",
            "energy_policy",
            "fossil_fuels",
            "renewable_energy",
            "environmental_regulation",
        ],
    },
    "political_identity": {
        "name": "Political Identity and Affiliation",
        "issues": [
            "party_affiliation",
            "political_self_identification",
            "campaign_activity",
            "political_endorsement",
        ],
    },
}


def get_dimension(name: str):
    return POLITICAL_DIMENSIONS.get(name)


def get_all_dimensions():
    return POLITICAL_DIMENSIONS