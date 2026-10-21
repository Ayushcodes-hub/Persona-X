import json
from datetime import datetime, timezone

from backend.app.core.database import SessionLocal
from backend.app.models.dossier import Dossier
from backend.app.models.evidence import Evidence
from backend.app.models.initiative import Initiative
from backend.app.models.person import Person
from backend.app.models.source import Source
from backend.app.models.statement import Statement
from backend.app.models.timeline import TimelineEvent


def seed_database():
    db = SessionLocal()
    try:
        # Check if already seeded with Dr. Eleanor Vance
        existing_vance = db.query(Person).filter(Person.canonical_name == "Dr. Eleanor Vance").first()
        if existing_vance:
            print("Database already seeded with core intelligence entities.")
            return

        print("Seeding PERSONA-X database with baseline intelligence entities...")

        # -------------------------------------------------------------
        # 1. Dr. Eleanor Vance (Astrophysicist)
        # -------------------------------------------------------------
        p1 = Person(
            canonical_name="Dr. Eleanor Vance",
            primary_profession="astrophysicist",
            identity_status="resolved",
            identity_confidence=0.98,
        )
        db.add(p1)
        db.flush()

        s1 = Source(
            url="https://cam.ac.uk/registry/alumni/vance",
            title="Cambridge University Doctoral Registry",
            publisher="Cambridge University Press",
            source_type="academic_registry",
            source_tier=1,
            reliability_score=0.99,
            is_verified=True,
        )
        s2 = Source(
            url="https://nature.com/articles/astronomy-kepler186f",
            title="Nature Astronomy — Atmospheric Signatures of Kepler-186f",
            publisher="Nature Publishing Group",
            source_type="peer_reviewed_journal",
            source_tier=1,
            reliability_score=0.98,
            is_verified=True,
        )
        s3 = Source(
            url="https://iau.org/news/announcements/2021/consortium",
            title="International Astronomy Council Gazette",
            publisher="IAU Communications",
            source_type="official_announcement",
            source_tier=1,
            reliability_score=0.96,
            is_verified=True,
        )
        db.add_all([s1, s2, s3])
        db.flush()

        e1 = Evidence(
            person_id=p1.id,
            source_id=s1.id,
            evidence_type="education",
            verification_status="verified",
            extracted_text="Defended doctoral thesis on non-equilibrium exoplanet atmospheric models with highest honors at Cambridge University.",
            confidence=0.99,
        )
        e2 = Evidence(
            person_id=p1.id,
            source_id=s2.id,
            evidence_type="discovery",
            verification_status="verified",
            extracted_text="Published definitive spectroscopic evidence of trace atmospheric water vapor on candidate exoplanet Kepler-186f.",
            confidence=0.97,
        )
        e3 = Evidence(
            person_id=p1.id,
            source_id=s3.id,
            evidence_type="appointment",
            verification_status="verified",
            extracted_text="Appointed Senior Research Director for the International Astrobiology Consortium to coordinate habitable zone surveys.",
            confidence=0.96,
        )
        db.add_all([e1, e2, e3])
        db.flush()

        # Timeline
        t1 = TimelineEvent(
            person_id=p1.id,
            evidence_id=e1.id,
            event_type="education",
            title="Ph.D. in Astrophysics & Planetary Science",
            description="Defended doctoral thesis on non-equilibrium exoplanet atmospheric models with highest honors.",
            start_date=datetime(2012, 9, 1, tzinfo=timezone.utc),
            end_date=datetime(2016, 6, 30, tzinfo=timezone.utc),
            organization="Cambridge University",
            location="Cambridge, UK",
            status="documented",
            confidence=0.99,
        )
        t2 = TimelineEvent(
            person_id=p1.id,
            evidence_id=e2.id,
            event_type="discovery",
            title="Kepler-186f Transmission Spectroscopy Breakthrough",
            description="Published definitive spectroscopic evidence of trace atmospheric water vapor.",
            start_date=datetime(2018, 5, 14, tzinfo=timezone.utc),
            organization="NASA Astrobiology Institute",
            location="Pasadena, CA",
            status="documented",
            confidence=0.97,
        )
        t3 = TimelineEvent(
            person_id=p1.id,
            evidence_id=e3.id,
            event_type="appointment",
            title="Chair of Planetary Exploration Consortium",
            description="Elected to direct multi-institutional telescope arrays for habitable zone surveys.",
            start_date=datetime(2021, 3, 1, tzinfo=timezone.utc),
            organization="Global Astronomical Union",
            location="Geneva, Switzerland",
            status="documented",
            confidence=0.96,
        )
        db.add_all([t1, t2, t3])

        # Statements
        st1 = Statement(
            person_id=p1.id,
            source_id=s2.id,
            evidence_id=e2.id,
            statement_type="direct_quote",
            text="The search for biosignatures in secondary atmospheres requires uncompromising evidentiary rigor; extraordinary claims require reproducible transmission spectra.",
            paraphrase="Advocated for strict spectroscopic reproducibility before declaring biosignature confirmation.",
            topic="scientific_methodology",
            context="Keynote address at the 2022 World Space Science Congress",
            attribution_status="attributed",
            confidence=0.98,
        )
        db.add(st1)

        # Initiatives
        init1 = Initiative(
            person_id=p1.id,
            evidence_id=e2.id,
            name="Habitable Exoplanet Spectral Database (HESD)",
            initiative_type="open_science_consortium",
            description="An open-access high-resolution database of simulated and observed exoplanetary absorption spectra.",
            objective="Accelerate atmospheric characterization through open scientific collaboration.",
            lifecycle_stage="active",
            start_date=datetime(2020, 1, 15, tzinfo=timezone.utc),
            evidence_confidence=0.95,
            verification_status="verified",
        )
        db.add(init1)

        # Dossier
        d1 = Dossier(
            person_id=p1.id,
            title="Intelligence Dossier: Dr. Eleanor Vance (Astrophysicist & Planetary Researcher)",
            status="verified",
            executive_summary="Dr. Eleanor Vance is an internationally recognized astrophysicist and planetary spectroscopist known for pioneering atmospheric characterization of terrestrial exoplanets. Verified records corroborate her leadership in the Kepler-186f biosignature research project and multiple peer-reviewed publications across Tier-1 scientific journals. Her public footprint is strictly scientific with no active political affiliations.",
            dossier_content=json.dumps({
                "biography": "Educated in theoretical astrophysics, Dr. Vance has served as Principal Investigator across major ground and space-based astronomical observatories. Her research focuses on transmission spectroscopy and the thermodynamic equilibria of habitable-zone exoplanetary atmospheres.",
                "core_milestones": [
                    "Discovered spectral water-vapor absorption signatures on candidate exoplanet Kepler-186f (2018).",
                    "Appointed Senior Research Director for the International Astrobiology Consortium (2021).",
                    "Awarded the Chandrasekhar Medal in Planetary Astronomy (2024).",
                ],
                "verified_standards": "Every factual assertion in this dossier has been grounded against cryptographically hashed snapshots with cite-or-drop verifier confidence exceeding 95%.",
            }),
            source_count=3,
            evidence_count=3,
            completeness_score=0.94,
        )
        db.add(d1)

        # -------------------------------------------------------------
        # 2. Jasprit Bumrah (Athlete)
        # -------------------------------------------------------------
        p2 = Person(
            canonical_name="Jasprit Bumrah",
            primary_profession="athlete",
            identity_status="resolved",
            identity_confidence=0.99,
        )
        db.add(p2)
        db.flush()

        sb1 = Source(
            url="https://icc-cricket.com/players/jasprit-bumrah",
            title="ICC Official Player Profile — Jasprit Bumrah",
            publisher="International Cricket Council",
            source_type="official_registry",
            source_tier=1,
            reliability_score=0.99,
            is_verified=True,
        )
        sb2 = Source(
            url="https://espncricinfo.com/cricketers/jasprit-bumrah-625383",
            title="ESPN Cricinfo — Jasprit Bumrah Career Record",
            publisher="ESPN Cricinfo",
            source_type="sports_journalism",
            source_tier=1,
            reliability_score=0.98,
            is_verified=True,
        )
        db.add_all([sb1, sb2])
        db.flush()

        eb1 = Evidence(
            person_id=p2.id,
            source_id=sb1.id,
            evidence_type="sports_career",
            verification_status="verified",
            extracted_text="International debut for India in ODI cricket against Australia in January 2016, establishing unique sling-arm action and lethal reverse swing.",
            confidence=0.99,
        )
        eb2 = Evidence(
            person_id=p2.id,
            source_id=sb2.id,
            evidence_type="milestone",
            verification_status="verified",
            extracted_text="Player of the Tournament at the 2024 ICC Men's T20 World Cup, conceding only 4.17 runs per over across the tournament.",
            confidence=0.98,
        )
        db.add_all([eb1, eb2])
        db.flush()

        tb1 = TimelineEvent(
            person_id=p2.id,
            evidence_id=eb1.id,
            event_type="career",
            title="International ODI & T20I Debut",
            description="Debuted for Indian national cricket team during the 2016 Australian tour in Sydney.",
            start_date=datetime(2016, 1, 23, tzinfo=timezone.utc),
            organization="BCCI / Indian Cricket Team",
            location="Sydney, Australia",
            status="documented",
            confidence=0.99,
        )
        tb2 = TimelineEvent(
            person_id=p2.id,
            evidence_id=eb2.id,
            event_type="achievement",
            title="ICC T20 World Cup Victory & Player of Tournament",
            description="Awarded ICC Player of the Tournament with 15 wickets at an economy rate of 4.17.",
            start_date=datetime(2024, 6, 29, tzinfo=timezone.utc),
            organization="International Cricket Council",
            location="Bridgetown, Barbados",
            status="documented",
            confidence=0.99,
        )
        db.add_all([tb1, tb2])

        stb1 = Statement(
            person_id=p2.id,
            source_id=sb1.id,
            evidence_id=eb2.id,
            statement_type="direct_quote",
            text="I usually try to keep things simple and execute what the team requires, focusing on clarity under pressure rather than the scoreboard.",
            paraphrase="Emphasized tactical clarity and execution over emotional pressure during championship matches.",
            topic="sports_psychology",
            context="Post-final press conference at Kensington Oval, Barbados",
            attribution_status="attributed",
            confidence=0.98,
        )
        db.add(stb1)

        db1 = Dossier(
            person_id=p2.id,
            title="Athletic Intelligence Dossier: Jasprit Bumrah (Pace Bowler & World Cup Champion)",
            status="verified",
            executive_summary="Jasprit Bumrah is widely recognized as one of cricket's premier all-format fast bowlers, holding historic number-one rankings across ICC Test, ODI, and T20I bowling charts. Verified records confirm his leadership in India's 2024 ICC T20 World Cup championship and multiple Indian Premier League titles. Consistent with PERSONA-X cite-or-drop neutrality, his public record contains zero documented political party affiliations or legislative stances.",
            dossier_content=json.dumps({
                "biography": "Born in Ahmedabad, Gujarat, Bumrah emerged through domestic cricket with Gujarat before breaking into international cricket in 2016. Renowned for his unique hyperextended bowling action and pinpoint yorkers.",
                "core_milestones": [
                    "Test Hat-trick against West Indies in Kingston, Jamaica (2019).",
                    "Ranked #1 ICC Test Bowler (2024).",
                    "Player of the Tournament at the ICC Men's T20 World Cup (2024).",
                ],
                "verified_standards": "All bowling figures, records, and press quotes verified against ICC and ESPN Cricinfo official archives.",
            }),
            source_count=2,
            evidence_count=2,
            completeness_score=0.93,
        )
        db.add(db1)

        # -------------------------------------------------------------
        # 3. Arvind Kejriwal (Politician)
        # -------------------------------------------------------------
        p3 = Person(
            canonical_name="Arvind Kejriwal",
            primary_profession="politician",
            identity_status="resolved",
            identity_confidence=0.99,
        )
        db.add(p3)
        db.flush()

        sk1 = Source(
            url="https://delhi.gov.in/cabinet/arvind-kejriwal",
            title="Government of NCT of Delhi — Chief Minister Secretariat Record",
            publisher="Delhi State Government",
            source_type="government_gazette",
            source_tier=1,
            reliability_score=0.99,
            is_verified=True,
        )
        sk2 = Source(
            url="https://eci.gov.in/affidavits/arvind-kejriwal",
            title="Election Commission of India — Candidate Declaration",
            publisher="Election Commission of India",
            source_type="electoral_commission",
            source_tier=1,
            reliability_score=0.99,
            is_verified=True,
        )
        db.add_all([sk1, sk2])
        db.flush()

        ek1 = Evidence(
            person_id=p3.id,
            source_id=sk1.id,
            evidence_type="governance_policy",
            verification_status="verified",
            extracted_text="Implemented state-funded lifeline water subsidies of 20,000 liters monthly and free electricity up to 200 units per household across Delhi.",
            confidence=0.98,
        )
        ek2 = Evidence(
            person_id=p3.id,
            source_id=sk1.id,
            evidence_type="healthcare_reform",
            verification_status="verified",
            extracted_text="Established over 500 neighborhood Aam Aadmi Mohalla Clinics providing decentralized primary healthcare and free essential diagnostic tests.",
            confidence=0.97,
        )
        db.add_all([ek1, ek2])
        db.flush()

        tk1 = TimelineEvent(
            person_id=p3.id,
            evidence_id=ek1.id,
            event_type="election",
            title="Sworn in as Chief Minister of Delhi",
            description="Formed state government following historic electoral victory on civic governance and anti-corruption platform.",
            start_date=datetime(2015, 2, 14, tzinfo=timezone.utc),
            organization="Government of NCT of Delhi",
            location="New Delhi, India",
            status="documented",
            confidence=0.99,
        )
        db.add(tk1)

        initk1 = Initiative(
            person_id=p3.id,
            evidence_id=ek2.id,
            name="Mohalla Clinics Primary Healthcare Network",
            initiative_type="civic_public_service",
            description="Decentralized neighborhood clinic system offering free primary consultations, diagnostics, and essential medicines.",
            objective="Provide universal free primary healthcare within walking distance of all urban households.",
            lifecycle_stage="active",
            start_date=datetime(2015, 10, 1, tzinfo=timezone.utc),
            evidence_confidence=0.96,
            verification_status="verified",
        )
        db.add(initk1)

        dk1 = Dossier(
            person_id=p3.id,
            title="Political Intelligence Dossier: Arvind Kejriwal (Civic Reformer & Political Leader)",
            status="verified",
            executive_summary="Arvind Kejriwal is an Indian civic leader and political figure who served three terms as Chief Minister of Delhi. Emerging from the 2011 India Against Corruption movement, his political platform combines center-left redistributive public utility subsidies (electricity, water, school reform) with populist civic anti-corruption governance. Documented legislative records confirm extensive public investments in neighborhood Mohalla clinics and public education infrastructure.",
            dossier_content=json.dumps({
                "biography": "Graduate of IIT Kharagpur and former Indian Revenue Service (IRS) officer, awarded the Ramon Magsaysay Award for Emergent Leadership in 2006 for grassroots RTI activism.",
                "core_milestones": [
                    "Founded Aam Aadmi Party (AAP) in November 2012.",
                    "Elected Chief Minister of Delhi in 2013, 2015, and 2020.",
                    "Expanded primary health through 500+ operational Mohalla clinics.",
                ],
                "verified_standards": "All legislative actions and policy programs cross-verified against official Delhi Gazette records.",
            }),
            source_count=2,
            evidence_count=2,
            completeness_score=0.95,
        )
        db.add(dk1)

        db.commit()
        print("PERSONA-X database successfully seeded with verified intelligence entities!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
