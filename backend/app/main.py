from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database.session import init_db
from app.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(
    title="SIH26034 — Packaged Commodity Compliance Screening API",
    description=(
        "Backend API for AI-assisted Packaged Commodity Compliance Screening under the "
        "Legal Metrology (Packaged Commodities) Rules, 2011.\n\n"
        "Integrates P1 (OCR/Extraction), P2 (Compliance Engine), P3 (Backend/Database), "
        "and P4 (Inspector Frontend)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration for local frontend development (P4) and decoupled production
is_wildcard = "*" in settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=not is_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Validation Error Handler (Pydantic / 422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        errors.append({
            "field": loc,
            "message": err.get("msg"),
            "type": err.get("type"),
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Extraction Schema Validation Failure",
            "errors": errors,
        },
    )

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Include core API router
app.include_router(api_router)

# Add API info endpoint directly under /api
@api_router.get("", tags=["Root"])
@api_router.get("/", tags=["Root"])
def api_root():
    return {
        "title": "SIH26034 Packaged Commodity Compliance Screening API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/health",
        "status": "active",
    }

# Frontend Static & SPA Serving (Unified Full-Stack Deployment)
if settings.SERVE_FRONTEND and settings.FRONTEND_DIR.exists():
    frontend_path = settings.FRONTEND_DIR
    src_path = frontend_path / "src"
    tests_path = frontend_path / "tests"

    if src_path.exists():
        app.mount("/src", StaticFiles(directory=str(src_path)), name="frontend_src")
    if tests_path.exists():
        app.mount("/tests", StaticFiles(directory=str(tests_path)), name="frontend_tests")

    @app.get("/", tags=["Frontend"])
    async def serve_frontend_root():
        return FileResponse(str(frontend_path / "index.html"))

    @app.get("/{full_path:path}", tags=["Frontend"])
    async def serve_spa_fallback(full_path: str):
        # Ignore API, docs, or openapi requests (FastAPI handles them or 404s)
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json")):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        target_file = frontend_path / full_path
        if target_file.is_file():
            return FileResponse(str(target_file))

        # Fallback to SPA index.html for client-side routing
        return FileResponse(str(frontend_path / "index.html"))

else:
    @app.get("/", tags=["Root"])
    def root():
        return {
            "title": "SIH26034 Packaged Commodity Compliance Screening API",
            "version": "1.0.0",
            "documentation": "/docs",
            "health": "/api/health",
            "status": "active",
        }
