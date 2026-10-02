from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.config import get_settings
from backend.app.core.database import engine
from backend.app.models import Base
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.dossier import router as dossier_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.persons import router as persons_router
from backend.app.api.routes.research import router as research_router
from backend.app.api.routes.system import router as system_router
from backend.app.services.research_worker import research_job_manager

settings = get_settings()

if settings.sentry_dsn:
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=settings.app_env,
        )
    except Exception as e:
        print("Sentry initialization skipped or failed:", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.app_env == "development":
        Base.metadata.create_all(bind=engine)

    research_job_manager.start()

    recovered_jobs = (
        research_job_manager.recover_stale_jobs()
    )

    if recovered_jobs:
        print(
            "PERSONA-X recovered research jobs:",
            recovered_jobs,
        )

    try:
        yield
    finally:
        research_job_manager.shutdown(
            wait=True,
        )


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "PERSONA-X — Universal Public-Person Research, "
        "Evidence Analysis, Force-Directed Graph Construction, "
        "Political Spectrum Analyzer, and Living Dossier Platform."
    ),
    lifespan=lifespan,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware for modern frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    research_router,
    prefix="/api/v1",
)

app.include_router(
    persons_router,
    prefix="/api/v1",
)

app.include_router(
    dossier_router,
    prefix="/api/v1",
)

app.include_router(
    system_router,
    prefix="/api/v1",
)

# SPA and Static Assets Mounting
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
FRONTEND_ASSETS = FRONTEND_DIST / "assets"

if FRONTEND_ASSETS.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_ASSETS)), name="assets")


@app.get("/favicon.svg", include_in_schema=False)
def favicon():
    fav = FRONTEND_DIST / "favicon.svg"
    if fav.exists():
        return FileResponse(str(fav), media_type="image/svg+xml")
    return Response(status_code=404)


@app.get("/app", include_in_schema=False)
@app.get("/app/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str = ""):
    index_html = FRONTEND_DIST / "index.html"
    if index_html.exists():
        return FileResponse(str(index_html))
    return {"message": "Frontend build not found. Run 'npm run build' inside frontend/"}


@app.get("/")
def root(request: Request):
    accept = request.headers.get("accept", "")
    index_html = FRONTEND_DIST / "index.html"
    if "text/html" in accept and index_html.exists():
        return FileResponse(str(index_html))

    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "online",
        "api": "/api/v1",
        "docs": "/docs",
        "app": "/app",
    }