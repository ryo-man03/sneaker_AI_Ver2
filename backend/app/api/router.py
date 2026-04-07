# file: app/api/router.py
from fastapi import APIRouter

from app.api.routers import auth, health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
