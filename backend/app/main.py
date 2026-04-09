# file: app/main.py
from importlib import import_module

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.settings import settings
from app.schemas.health import HealthResponse
from app.services.alert_scheduler import start_alert_scheduler, stop_alert_scheduler

init_db_and_seed = import_module("app.db.session").init_db_and_seed

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.on_event("startup")
async def startup() -> None:
    await init_db_and_seed()
    await start_alert_scheduler()


@app.on_event("shutdown")
async def shutdown() -> None:
    await stop_alert_scheduler()


@app.get("/health", response_model=HealthResponse)
def health_root() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
    )
