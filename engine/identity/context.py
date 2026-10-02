from dataclasses import dataclass, field
from typing import List, Optional

from engine.identity.schemas import IdentityResolution


@dataclass
class IdentityContext:
    canonical_name: Optional[str] = None
    profession: Optional[str] = None
    nationality: Optional[str] = None
    organization: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    is_verified: bool = False


class IdentityContextBuilder:
    """Build conservative query context from a verified identity resolution.

    No identity facts are invented here. Only fields explicitly present on
    a resolved IdentityResolution are exposed to downstream research.
    """

    def build(self, resolution: IdentityResolution) -> IdentityContext:
        if resolution.status != "resolved":
            return IdentityContext(is_verified=False)

        if not resolution.candidates:
            return IdentityContext(is_verified=False)

        candidate = resolution.candidates[0]

        aliases = []
        if candidate.name and resolution.canonical_name:
            if candidate.name.strip().lower() != resolution.canonical_name.strip().lower():
                aliases.append(candidate.name.strip())

        return IdentityContext(
            canonical_name=resolution.canonical_name,
            profession=candidate.profession,
            nationality=candidate.nationality,
            organization=candidate.organization,
            location=candidate.location,
            birth_date=candidate.birth_date,
            aliases=aliases,
            is_verified=True,
        )