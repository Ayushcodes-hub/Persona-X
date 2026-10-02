from typing import Dict, List


UNIVERSAL_RESEARCH_AREAS: Dict[str, Dict[str, object]] = {
    "identity": {
        "query_type": "identity",
        "priority": 10,
        "source_quality": "primary_preferred",
        "description": "Establish the person's identity, aliases, and disambiguating information.",
    },
    "biography": {
        "query_type": "biography",
        "priority": 9,
        "source_quality": "primary_or_major_secondary",
        "description": "Research documented biographical background and major life history.",
    },
    "education": {
        "query_type": "education",
        "priority": 8,
        "source_quality": "primary_or_major_secondary",
        "description": "Research documented education, training, qualifications, and relevant institutions.",
    },
    "career": {
        "query_type": "career",
        "priority": 10,
        "source_quality": "primary_or_major_secondary",
        "description": "Establish the person's professional career and major career transitions.",
    },
    "affiliations": {
        "query_type": "affiliation",
        "priority": 8,
        "source_quality": "primary_preferred",
        "description": "Identify documented organizations, institutions, teams, companies, parties, or other affiliations.",
    },
    "statements": {
        "query_type": "public_statement",
        "priority": 9,
        "source_quality": "primary_preferred",
        "description": "Find attributable public statements, interviews, speeches, publications, or official remarks.",
    },
    "initiatives": {
        "query_type": "initiative",
        "priority": 8,
        "source_quality": "primary_preferred",
        "description": "Research initiatives, programs, projects, campaigns, foundations, or other activities associated with the person.",
    },
    "achievements": {
        "query_type": "achievement",
        "priority": 8,
        "source_quality": "primary_or_major_secondary",
        "description": "Research documented achievements, awards, records, discoveries, products, publications, or milestones.",
    },
    "public_activity": {
        "query_type": "public_activity",
        "priority": 6,
        "source_quality": "primary_or_major_secondary",
        "description": "Research significant public-facing activities outside the person's core career.",
    },
    "disputed_matters": {
        "query_type": "disputed_matter",
        "priority": 5,
        "source_quality": "major_secondary_or_primary",
        "description": "Identify documented disputes, allegations, corrections, investigations, or contested claims requiring careful verification.",
    },
}


PROFESSION_RESEARCH_AREAS: Dict[str, Dict[str, Dict[str, object]]] = {
    "athlete": {
        "teams_and_competitions": {
            "query_type": "sporting_career",
            "priority": 10,
            "source_quality": "primary_or_major_secondary",
            "description": "Teams, leagues, competitions, selections, seasons, and participation.",
        },
        "performance_records": {
            "query_type": "sporting_record",
            "priority": 10,
            "source_quality": "official_statistics_preferred",
            "description": "Official statistics, records, rankings, results, and performance milestones.",
        },
        "awards": {
            "query_type": "sporting_award",
            "priority": 8,
            "source_quality": "official_or_major_secondary",
            "description": "Awards, honors, selections, and recognitions.",
        },
        "interviews": {
            "query_type": "athlete_interview",
            "priority": 7,
            "source_quality": "primary_or_major_secondary",
            "description": "Interviews concerning career, sport, training, and public views.",
        },
        "endorsements": {
            "query_type": "endorsement",
            "priority": 5,
            "source_quality": "primary_or_major_secondary",
            "description": "Documented commercial endorsements and brand relationships.",
        },
        "philanthropy": {
            "query_type": "philanthropy",
            "priority": 6,
            "source_quality": "primary_or_major_secondary",
            "description": "Documented charitable, community, or social initiatives.",
        },
    },
    "actor": {
        "filmography": {
            "query_type": "filmography",
            "priority": 10,
            "source_quality": "official_or_major_secondary",
            "description": "Films, television, streaming, theatre, and other acting credits.",
        },
        "awards": {
            "query_type": "acting_award",
            "priority": 8,
            "source_quality": "official_or_major_secondary",
            "description": "Awards, nominations, and recognized performances.",
        },
        "interviews": {
            "query_type": "actor_interview",
            "priority": 8,
            "source_quality": "primary_or_major_secondary",
            "description": "Interviews and attributable statements about career and public matters.",
        },
        "production": {
            "query_type": "production_activity",
            "priority": 6,
            "source_quality": "primary_or_major_secondary",
            "description": "Production, directing, writing, or ownership activities.",
        },
        "endorsements": {
            "query_type": "endorsement",
            "priority": 5,
            "source_quality": "primary_or_major_secondary",
            "description": "Commercial endorsements and brand relationships.",
        },
        "philanthropy": {
            "query_type": "philanthropy",
            "priority": 6,
            "source_quality": "primary_or_major_secondary",
            "description": "Documented charitable and social initiatives.",
        },
    },
    "scientist": {
        "research": {
            "query_type": "scientific_research",
            "priority": 10,
            "source_quality": "academic_or_primary",
            "description": "Research fields, major research programs, and documented scientific contributions.",
        },
        "publications": {
            "query_type": "publication",
            "priority": 10,
            "source_quality": "academic_or_primary",
            "description": "Peer-reviewed publications, books, reports, and other scholarly work.",
        },
        "patents": {
            "query_type": "patent",
            "priority": 7,
            "source_quality": "official_or_academic",
            "description": "Documented patents and intellectual-property activity where applicable.",
        },
        "discoveries": {
            "query_type": "scientific_discovery",
            "priority": 9,
            "source_quality": "academic_or_major_secondary",
            "description": "Documented discoveries, inventions, methods, or scientific contributions.",
        },
        "awards": {
            "query_type": "scientific_award",
            "priority": 8,
            "source_quality": "official_or_academic",
            "description": "Scientific prizes, fellowships, honors, and recognitions.",
        },
        "lectures_and_outreach": {
            "query_type": "science_outreach",
            "priority": 5,
            "source_quality": "primary_or_academic",
            "description": "Public lectures, educational outreach, and science communication.",
        },
    },
    "entrepreneur": {
        "companies": {
            "query_type": "company_history",
            "priority": 10,
            "source_quality": "primary_or_major_secondary",
            "description": "Companies founded, led, acquired, invested in, or otherwise materially associated with the person.",
        },
        "funding": {
            "query_type": "funding",
            "priority": 8,
            "source_quality": "primary_or_major_secondary",
            "description": "Documented funding rounds, investors, financing, and capital events.",
        },
        "products": {
            "query_type": "product",
            "priority": 8,
            "source_quality": "primary_or_major_secondary",
            "description": "Products, services, launches, and major product milestones.",
        },
        "investments": {
            "query_type": "investment",
            "priority": 6,
            "source_quality": "primary_or_major_secondary",
            "description": "Documented investments, acquisitions, and investment vehicles.",
        },
        "business_statements": {
            "query_type": "business_statement",
            "priority": 8,
            "source_quality": "primary_preferred",
            "description": "Public statements about business strategy, technology, markets, and management.",
        },
        "philanthropy": {
            "query_type": "philanthropy",
            "priority": 6,
            "source_quality": "primary_or_major_secondary",
            "description": "Documented philanthropic organizations, donations, and initiatives.",
        },
    },
    "politician": {
        "elections": {
            "query_type": "election",
            "priority": 10,
            "source_quality": "official_election_source_preferred",
            "description": "Elections contested, results, offices sought, and electoral history.",
        },
        "offices": {
            "query_type": "public_office",
            "priority": 10,
            "source_quality": "official_source_preferred",
            "description": "Public offices held, dates, jurisdictions, and responsibilities.",
        },
        "legislation": {
            "query_type": "legislation",
            "priority": 10,
            "source_quality": "official_legislative_source_preferred",
            "description": "Bills sponsored, introduced, supported, opposed, enacted, or otherwise documented.",
        },
        "votes": {
            "query_type": "legislative_vote",
            "priority": 10,
            "source_quality": "official_legislative_source_preferred",
            "description": "Documented voting records where reliable vote records exist.",
        },
        "policies": {
            "query_type": "policy_position",
            "priority": 10,
            "source_quality": "primary_preferred",
            "description": "Documented policy positions and proposals, with dates and source context.",
        },
        "speeches": {
            "query_type": "political_speech",
            "priority": 9,
            "source_quality": "primary_preferred",
            "description": "Official speeches, debates, addresses, and public remarks.",
        },
        "party_affiliation": {
            "query_type": "party_affiliation",
            "priority": 9,
            "source_quality": "official_source_preferred",
            "description": "Documented party membership, candidacies, offices, and organizational roles.",
        },
    },
    "journalist": {
        "publications": {
            "query_type": "journalism_publication",
            "priority": 10,
            "source_quality": "primary_or_major_secondary",
            "description": "Published journalism, columns, investigations, broadcasts, or other journalistic work.",
        },
        "investigations": {
            "query_type": "journalistic_investigation",
            "priority": 9,
            "source_quality": "primary_or_major_secondary",
            "description": "Major documented investigative projects and reporting.",
        },
        "interviews": {
            "query_type": "journalist_interview",
            "priority": 7,
            "source_quality": "primary_or_major_secondary",
            "description": "Interviews and attributable public statements.",
        },
        "editorial_roles": {
            "query_type": "editorial_role",
            "priority": 7,
            "source_quality": "primary_or_major_secondary",
            "description": "Editorial leadership, newsroom positions, and professional affiliations.",
        },
    },
    "author": {
        "bibliography": {
            "query_type": "bibliography",
            "priority": 10,
            "source_quality": "publisher_or_primary",
            "description": "Books, essays, publications, and major works.",
        },
        "literary_awards": {
            "query_type": "literary_award",
            "priority": 7,
            "source_quality": "official_or_major_secondary",
            "description": "Literary awards, nominations, and recognitions.",
        },
        "interviews": {
            "query_type": "author_interview",
            "priority": 7,
            "source_quality": "primary_or_major_secondary",
            "description": "Interviews and attributable statements about writing and public topics.",
        },
        "public_lectures": {
            "query_type": "literary_lecture",
            "priority": 5,
            "source_quality": "primary_or_academic",
            "description": "Lectures, readings, talks, and public intellectual activity.",
        },
    },
    "academic": {
        "research": {
            "query_type": "academic_research",
            "priority": 10,
            "source_quality": "academic_or_primary",
            "description": "Research fields, projects, findings, and scholarly contributions.",
        },
        "publications": {
            "query_type": "academic_publication",
            "priority": 10,
            "source_quality": "academic_or_primary",
            "description": "Scholarly publications and research outputs.",
        },
        "teaching": {
            "query_type": "teaching",
            "priority": 7,
            "source_quality": "institutional_or_primary",
            "description": "Documented teaching roles, courses, supervision, and academic responsibilities.",
        },
        "awards": {
            "query_type": "academic_award",
            "priority": 7,
            "source_quality": "institutional_or_academic",
            "description": "Academic awards, fellowships, honors, and recognitions.",
        },
    },
    "artist": {
        "works": {
            "query_type": "artistic_work",
            "priority": 10,
            "source_quality": "primary_or_major_secondary",
            "description": "Major artworks, exhibitions, performances, collections, or artistic works.",
        },
        "exhibitions": {
            "query_type": "exhibition",
            "priority": 8,
            "source_quality": "institutional_or_primary",
            "description": "Documented exhibitions, galleries, museums, and artistic events.",
        },
        "awards": {
            "query_type": "art_award",
            "priority": 7,
            "source_quality": "official_or_major_secondary",
            "description": "Awards, honors, residencies, and recognitions.",
        },
        "artist_statements": {
            "query_type": "artist_statement",
            "priority": 8,
            "source_quality": "primary_preferred",
            "description": "Artist statements, interviews, lectures, and attributable commentary.",
        },
    },
}


POLITICAL_RESEARCH_AREAS: Dict[str, Dict[str, object]] = {
    "political_activity": {
        "query_type": "political_activity",
        "priority": 8,
        "source_quality": "primary_or_major_secondary",
        "description": "Documented political activity, campaigns, political organizations, or public political participation.",
    },
    "public_policy": {
        "query_type": "public_policy",
        "priority": 8,
        "source_quality": "primary_or_major_secondary",
        "description": "Documented positions or activities concerning public policy.",
    },
    "political_statements": {
        "query_type": "political_statement",
        "priority": 8,
        "source_quality": "primary_preferred",
        "description": "Attributable statements concerning political institutions, elections, government, or public policy.",
    },
    "political_endorsements": {
        "query_type": "political_endorsement",
        "priority": 7,
        "source_quality": "primary_or_major_secondary",
        "description": "Documented endorsements or support for political candidates, parties, or ballot positions.",
    },
}