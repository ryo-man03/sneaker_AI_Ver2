# file: app/models/sneaker.py
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Sneaker(Base):
    __tablename__ = "sneakers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    model: Mapped[str] = mapped_column(String(255))
    brand: Mapped[str] = mapped_column(String(128), index=True)
    retail_price: Mapped[float] = mapped_column(Float)
    market_price: Mapped[float] = mapped_column(Float)
    buy_score: Mapped[int] = mapped_column(Integer)
    liquidity: Mapped[str] = mapped_column(String(16))
    note: Mapped[str] = mapped_column(String(255), default="")
