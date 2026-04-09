# file: alembic/versions/20260408_0001_core_data.py
"""core data initial tables

Revision ID: 20260408_0001
Revises:
Create Date: 2026-04-08
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260408_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sneakers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=False),
        sa.Column("brand", sa.String(length=128), nullable=False),
        sa.Column("retail_price", sa.Float(), nullable=False),
        sa.Column("market_price", sa.Float(), nullable=False),
        sa.Column("buy_score", sa.Integer(), nullable=False),
        sa.Column("liquidity", sa.String(length=16), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sneakers_brand"), "sneakers", ["brand"], unique=False)
    op.create_index(op.f("ix_sneakers_sku"), "sneakers", ["sku"], unique=True)

    op.create_table(
        "market_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("period", sa.String(length=16), nullable=False),
        sa.Column("ask_price", sa.Float(), nullable=False),
        sa.Column("bid_price", sa.Float(), nullable=False),
        sa.Column("last_sale", sa.Float(), nullable=False),
        sa.Column("liquidity", sa.String(length=16), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_market_snapshots_period"), "market_snapshots", ["period"], unique=False)
    op.create_index(op.f("ix_market_snapshots_sku"), "market_snapshots", ["sku"], unique=False)

    op.create_table(
        "stock_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("company", sa.String(length=128), nullable=False),
        sa.Column("period", sa.String(length=16), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("change_pct", sa.Float(), nullable=False),
        sa.Column("index_name", sa.String(length=64), nullable=False),
        sa.Column("index_change_pct", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stock_snapshots_period"), "stock_snapshots", ["period"], unique=False)
    op.create_index(op.f("ix_stock_snapshots_ticker"), "stock_snapshots", ["ticker"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_stock_snapshots_ticker"), table_name="stock_snapshots")
    op.drop_index(op.f("ix_stock_snapshots_period"), table_name="stock_snapshots")
    op.drop_table("stock_snapshots")

    op.drop_index(op.f("ix_market_snapshots_sku"), table_name="market_snapshots")
    op.drop_index(op.f("ix_market_snapshots_period"), table_name="market_snapshots")
    op.drop_table("market_snapshots")

    op.drop_index(op.f("ix_sneakers_sku"), table_name="sneakers")
    op.drop_index(op.f("ix_sneakers_brand"), table_name="sneakers")
    op.drop_table("sneakers")
