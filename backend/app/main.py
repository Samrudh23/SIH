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

# CORS Configuration for local frontend development (P4)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
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

# Include core API router
app.include_router(api_router)

@app.get("/", tags=["Root"])
def root():
    return {
        "title": "SIH26034 Packaged Commodity Compliance Screening API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/health",
        "status": "active",
    }
