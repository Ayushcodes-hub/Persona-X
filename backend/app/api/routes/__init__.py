from backend.app.api.routes.dossier import router as dossier_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.research import router as research_router

__all__ = [
    "dossier_router",
    "health_router",
    "research_router",
]