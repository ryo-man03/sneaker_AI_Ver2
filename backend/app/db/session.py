# file: app/db/session.py
import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import event, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import settings
from app.db.base import Base
from app.models.closet import ClosetItem
from app.models.market import MarketSnapshot
from app.models.notification_event import NotificationEvent
from app.models.price_alert import PriceAlertRule
from app.models.sneaker import Sneaker
from app.models.stock import StockSnapshot
from app.models.wishlist import WishlistItem

engine = create_async_engine(settings.database_url, future=True)
_db_ready = False
_db_lock = asyncio.Lock()

if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection: Any, _connection_record: object) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute(f"PRAGMA busy_timeout={settings.sqlite_busy_timeout_ms};")
        cursor.close()


SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    await ensure_db_ready()
    async with SessionLocal() as session:
        yield session


async def init_db_and_seed() -> None:
    await ensure_db_ready()


async def ensure_db_ready() -> None:
    global _db_ready
    if _db_ready:
        return

    async with _db_lock:
        if _db_ready:
            return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        sneaker_count = await session.scalar(select(func.count()).select_from(Sneaker))
        if not sneaker_count or sneaker_count == 0:
            _seed_core_data(session)

        await _seed_asset_data_if_empty(session)
        await session.commit()
        _db_ready = True


def _seed_core_data(session: AsyncSession) -> None:
    now = datetime.now(UTC)
    sneakers = [
        Sneaker(
            sku="555088-001",
            model='Air Jordan 1 Retro High OG "Bred"',
            brand="NIKE",
            retail_price=16500,
            market_price=48500,
            buy_score=89,
            liquidity="高",
            note="2024 Restock",
        ),
        Sneaker(
            sku="HQ4540",
            model='Yeezy Boost 350 V2 "Onyx"',
            brand="ADIDAS",
            retail_price=27500,
            market_price=32000,
            buy_score=62,
            liquidity="中",
            note="明日発売予定",
        ),
        Sneaker(
            sku="U9060AAA",
            model='New Balance 9060 "Sea Salt"',
            brand="NEW BALANCE",
            retail_price=19800,
            market_price=21000,
            buy_score=77,
            liquidity="高",
            note="在庫あり",
        ),
    ]
    session.add_all(sneakers)

    session.add_all(
        [
            MarketSnapshot(
                sku="555088-001",
                period="1d",
                ask_price=48500,
                bid_price=46000,
                last_sale=47200,
                liquidity="高",
                updated_at=now,
            ),
            MarketSnapshot(
                sku="HQ4540",
                period="1d",
                ask_price=32000,
                bid_price=28000,
                last_sale=30500,
                liquidity="中",
                updated_at=now,
            ),
            MarketSnapshot(
                sku="U9060AAA",
                period="1d",
                ask_price=21000,
                bid_price=19800,
                last_sale=20400,
                liquidity="高",
                updated_at=now,
            ),
        ]
    )

    session.add_all(
        [
            StockSnapshot(
                ticker="NKE",
                company="Nike",
                period="1d",
                price=98.4,
                change_pct=1.2,
                index_name="NIKKEI",
                index_change_pct=0.4,
                updated_at=now,
            ),
            StockSnapshot(
                ticker="ADDYY",
                company="Adidas",
                period="1d",
                price=120.8,
                change_pct=-0.8,
                index_name="NIKKEI",
                index_change_pct=0.4,
                updated_at=now,
            ),
            StockSnapshot(
                ticker="ONON",
                company="On Running",
                period="1d",
                price=41.2,
                change_pct=3.4,
                index_name="NIKKEI",
                index_change_pct=0.4,
                updated_at=now,
            ),
        ]
    )


async def _seed_asset_data_if_empty(session: AsyncSession) -> None:
    wishlist_count = await session.scalar(select(func.count()).select_from(WishlistItem))
    closet_count = await session.scalar(select(func.count()).select_from(ClosetItem))
    alert_count = await session.scalar(select(func.count()).select_from(PriceAlertRule))
    await session.scalar(select(func.count()).select_from(NotificationEvent))

    if not wishlist_count or wishlist_count == 0:
        session.add(
            WishlistItem(
                sku="HQ4540",
                model='Yeezy Boost 350 V2 "Onyx"',
                brand="ADIDAS",
                target_price=29500,
                current_price=32000,
                note="価格下落待ち",
            )
        )

    if not closet_count or closet_count == 0:
        session.add(
            ClosetItem(
                sku="555088-001",
                model='Air Jordan 1 Retro High OG "Bred"',
                brand="NIKE",
                quantity=1,
                avg_buy_price=43500,
                current_price=48500,
            )
        )

    if not alert_count or alert_count == 0:
        session.add(
            PriceAlertRule(
                sku="HQ4540",
                rule_type="price_below",
                threshold=29500,
                active=True,
                cooldown_minutes=180,
            )
        )
