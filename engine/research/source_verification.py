from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass
class SourceVerification:
    source_tier: int
    source_type: str
    authority_class: str
    reason: str
    confidence: float


class SourceVerifier:
    PRIMARY_DOMAINS = {
        "gov",
        "gov.in",
        "gov.uk",
        "gov.au",
        "gov.ca",
        "europa.eu",
        "who.int",
        "un.org",
        "worldbank.org",
        "imf.org",
        "sec.gov",
        "supremecourt.gov",
        "congress.gov",
        "parliament.uk",
    }

    ACADEMIC_DOMAINS = {
        "edu",
        "ac.uk",
        "ac.in",
        "ac.jp",
        "nature.com",
        "science.org",
        "sciencedirect.com",
        "springer.com",
        "jstor.org",
    }

    MAJOR_NEWS_DOMAINS = {
        "reuters.com",
        "apnews.com",
        "bbc.com",
        "bbc.co.uk",
        "nytimes.com",
        "washingtonpost.com",
        "wsj.com",
        "ft.com",
        "bloomberg.com",
        "economist.com",
    }

    OFFICIAL_PATH_SIGNALS = {
        "/about/",
        "/about",
        "/leadership/",
        "/leadership",
        "/investor/",
        "/investor",
        "/investors/",
        "/investors",
        "/newsroom/",
        "/newsroom",
        "/press/",
        "/press",
        "/source/",
        "/source",
        "/official/",
        "/official",
        "/company/",
        "/company",
        "/corporate/",
        "/corporate",
        "/annual-report",
        "/annual_report",
    }

    def extract_domain(self, url: str) -> str:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    def domain_matches(self, domain: str, candidate: str) -> bool:
        return domain == candidate or domain.endswith("." + candidate)

    def has_official_path_signal(self, url: str) -> bool:
        path = urlparse(url).path.lower()

        return any(
            signal in path
            for signal in self.OFFICIAL_PATH_SIGNALS
        )

    def classify(
        self,
        url: str,
        title: Optional[str] = None,
    ) -> SourceVerification:

        domain = self.extract_domain(url)
        parsed = urlparse(url)
        title_lower = (title or "").lower()

        # Government, courts, legislatures and major international institutions.
        for candidate in self.PRIMARY_DOMAINS:
            if self.domain_matches(domain, candidate):
                return SourceVerification(
                    source_tier=1,
                    source_type="primary_institutional",
                    authority_class="official",
                    reason=(
                        "Domain matches an authoritative government, "
                        f"institutional, legislative, judicial, or international source: {candidate}"
                    ),
                    confidence=0.98,
                )

        # Academic and research institutions/publications.
        for candidate in self.ACADEMIC_DOMAINS:
            if self.domain_matches(domain, candidate):
                return SourceVerification(
                    source_tier=2,
                    source_type="academic_or_research",
                    authority_class="research",
                    reason=(
                        "Domain matches an academic, scientific, "
                        f"or research source: {candidate}"
                    ),
                    confidence=0.95,
                )

        # Established journalism.
        for candidate in self.MAJOR_NEWS_DOMAINS:
            if self.domain_matches(domain, candidate):
                return SourceVerification(
                    source_tier=2,
                    source_type="major_news",
                    authority_class="journalistic",
                    reason=(
                        "Domain matches an established news organization: "
                        f"{candidate}"
                    ),
                    confidence=0.95,
                )

        # Professional profiles.
        if self.domain_matches(domain, "linkedin.com"):
            return SourceVerification(
                source_tier=3,
                source_type="professional_profile",
                authority_class="self_or_professional",
                reason=(
                    "Professional networking profile; useful for identity "
                    "and career evidence but requires corroboration."
                ),
                confidence=0.85,
            )

        # Encyclopedic secondary source.
        if self.domain_matches(domain, "wikipedia.org"):
            return SourceVerification(
                source_tier=3,
                source_type="encyclopedic_secondary",
                authority_class="secondary",
                reason=(
                    "Useful secondary reference; important claims should "
                    "be corroborated with primary or authoritative sources."
                ),
                confidence=0.95,
            )

        # Official organizational pages.
        #
        # This is deliberately based on URL structure rather than a
        # particular company/person. It therefore works across companies,
        # universities, sports organizations, NGOs, institutions, etc.
        if self.has_official_path_signal(url):
            return SourceVerification(
                source_tier=2,
                source_type="organizational_source",
                authority_class="organization",
                reason=(
                    "URL contains a recognized official organizational "
                    "publication or leadership path."
                ),
                confidence=0.85,
            )

        # Common official subdomains.
        official_subdomains = (
            "news.",
            "about.",
            "investor.",
            "investors.",
            "press.",
            "leadership.",
            "corporate.",
        )

        if any(domain.startswith(prefix) for prefix in official_subdomains):
            return SourceVerification(
                source_tier=2,
                source_type="organizational_source",
                authority_class="organization",
                reason=(
                    "Domain uses a common official organizational "
                    "subdomain pattern."
                ),
                confidence=0.80,
            )

        return SourceVerification(
            source_tier=4,
            source_type="general_web",
            authority_class="unclassified",
            reason=(
                "No authoritative source classification rule matched; "
                "independent corroboration is required."
            ),
            confidence=0.50,
        )