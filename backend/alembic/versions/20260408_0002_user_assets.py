# file: alembic/versions/20260408_0002_user_assets.py
"""user asset tables for phase4

Revision ID: 20260408_0002
Revises: 20260408_0001
Create Date: 2026-04-08
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260408_0002"
down_revision: str | None = "20260408_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    if "wishlist_items" not in existing:
        op.create_table(
            "wishlist_items",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("sku", sa.String(length=64), nullable=False),
            sa.Column("model", sa.String(length=255), nullable=False),
            sa.Column("brand", sa.String(length=128), nullable=False),
            sa.Column("target_price", sa.Float(), nullable=False),
            sa.Column("current_price", sa.Float(), nullable=False),
            sa.Column("note", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if "closet_items" not in existing:
        op.create_table(
            "closet_items",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("sku", sa.String(length=64), nullable=False),
            sa.Column("model", sa.String(length=255), nullable=False),
            sa.Column("brand", sa.String(length=128), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False),
            sa.Column("avg_buy_price", sa.Float(), nullable=False),
            sa.Column("current_price", sa.Float(), nullable=False),
            sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if "price_alert_rules" not in existing:
        op.create_table(
            "price_alert_rules",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("sku", sa.String(length=64), nullable=False),
            sa.Column("rule_type", sa.String(length=32), nullable=False),
            sa.Column("threshold", sa.Float(), nullable=False),
            sa.Column("active", sa.Boolean(), nullable=False),
            sa.Column("cooldown_minutes", sa.Integer(), nullable=False),
            sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    wishlist_indexes = {index["name"] for index in inspector.get_indexes("wishlist_items")}
    closet_indexes = {index["name"] for index in inspector.get_indexes("closet_items")}
    alert_indexes = {index["name"] for index in inspector.get_indexes("price_alert_rules")}

    wishlist_brand_index = op.f("ix_wishlist_items_brand")
    wishlist_sku_index = op.f("ix_wishlist_items_sku")
    if wishlist_brand_index not in wishlist_indexes:
        op.create_index(wishlist_brand_index, "wishlist_items", ["brand"], unique=False)
    if wishlist_sku_index not in wishlist_indexes:
        op.create_index(wishlist_sku_index, "wishlist_items", ["sku"], unique=False)

    closet_brand_index = op.f("ix_closet_items_brand")
    closet_sku_index = op.f("ix_closet_items_sku")
    if closet_brand_index not in closet_indexes:
        op.create_index(closet_brand_index, "closet_items", ["brand"], unique=False)
    if closet_sku_index not in closet_indexes:
        op.create_index(closet_sku_index, "closet_items", ["sku"], unique=False)

    alert_sku_index = op.f("ix_price_alert_rules_sku")
    if alert_sku_index not in alert_indexes:
        op.create_index(alert_sku_index, "price_alert_rules", ["sku"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    if "price_alert_rules" in existing:
        indexes = {index["name"] for index in inspector.get_indexes("price_alert_rules")}
        if op.f("ix_price_alert_rules_sku") in indexes:
            op.drop_index(op.f("ix_price_alert_rules_sku"), table_name="price_alert_rules")
        op.drop_table("price_alert_rules")

    if "closet_items" in existing:
        indexes = {index["name"] for index in inspector.get_indexes("closet_items")}
        if op.f("ix_closet_items_sku") in indexes:
            op.drop_index(op.f("ix_closet_items_sku"), table_name="closet_items")
        if op.f("ix_closet_items_brand") in indexes:
            op.drop_index(op.f("ix_closet_items_brand"), table_name="closet_items")
        op.drop_table("closet_items")

    if "wishlist_items" in existing:
        indexes = {index["name"] for index in inspector.get_indexes("wishlist_items")}
        if op.f("ix_wishlist_items_sku") in indexes:
            op.drop_index(op.f("ix_wishlist_items_sku"), table_name="wishlist_items")
        if op.f("ix_wishlist_items_brand") in indexes:
            op.drop_index(op.f("ix_wishlist_items_brand"), table_name="wishlist_items")
        op.drop_table("wishlist_items")
