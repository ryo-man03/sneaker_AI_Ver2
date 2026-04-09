# file: app/api/router.py
from fastapi import APIRouter

from app.api.routers import auth, health
from app.api.routers.alerts import router as alerts_router
from app.api.routers.closet import router as closet_router
from app.api.routers.image_analysis import router as image_analysis_router
from app.api.routers.instagram import router as instagram_router
from app.api.routers.intelligence import router as intelligence_router
from app.api.routers.market import router as market_router
from app.api.routers.notifications import router as notifications_router
from app.api.routers.portfolio import router as portfolio_router
from app.api.routers.search import router as search_router
from app.api.routers.search_grounding import router as search_grounding_router
from app.api.routers.sneakers import router as sneakers_router
from app.api.routers.stocks import router as stocks_router
from app.api.routers.wishlist import router as wishlist_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(sneakers_router)
api_router.include_router(search_router)
api_router.include_router(market_router)
api_router.include_router(stocks_router)
api_router.include_router(intelligence_router)
api_router.include_router(image_analysis_router)
api_router.include_router(search_grounding_router)
api_router.include_router(instagram_router)
api_router.include_router(wishlist_router)
api_router.include_router(closet_router)
api_router.include_router(portfolio_router)
api_router.include_router(alerts_router)
api_router.include_router(notifications_router)
