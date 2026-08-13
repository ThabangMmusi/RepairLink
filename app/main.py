from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import get_settings
from app.database import create_tables
from app.models import ReportCategory, Urgency
from app.routers.reports import router as reports_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    yield


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="A single-user REST service for reporting and tracking campus and residence maintenance problems.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(reports_router)


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"name": settings.app_name, "docs": "/docs", "health": "/health"}


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/locations", tags=["metadata"])
def locations() -> list[str]:
    return [
        "Main Campus - Library",
        "Main Campus - Computer Laboratory",
        "Main Campus - Student Centre",
        "Off-Campus Residence - Block A",
        "Off-Campus Residence - Block B",
        "Off-Campus Residence - Common Area",
    ]


@app.get("/api/categories", tags=["metadata"])
def categories() -> dict[str, list[str]]:
    return {"categories": [category.value for category in ReportCategory], "urgencies": [urgency.value for urgency in Urgency]}
