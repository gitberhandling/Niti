from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.core.exceptions import (
    NitiException,
    niti_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.db.database import init_db

# ─── API Routers ──────────────────────────────────────────
from app.api import auth, projects, milestones, documents, biometric, fraud, audit

app = FastAPI(
    title="NitiLedger API",
    description=(
        "Blockchain-based government project transparency and fraud detection system. "
        "All routes are protected by JWT (Keycloak) and RBAC middleware."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ─── Middleware (order matters — outermost first) ──────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# ─── Exception Handlers ────────────────────────────────────
app.add_exception_handler(NitiException, niti_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ─── Routers ───────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(milestones.router)
app.include_router(documents.router)
app.include_router(biometric.router)
app.include_router(fraud.router)
app.include_router(audit.router)

# ─── Prometheus Metrics ────────────────────────────────────
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# ─── Startup / Shutdown ────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/health", tags=["Health"], summary="Health check")
async def health():
    return {"status": "ok", "service": "niti-backend", "version": "1.0.0"}
