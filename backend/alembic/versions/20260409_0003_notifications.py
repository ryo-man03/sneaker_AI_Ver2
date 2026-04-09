# file: alembic/versions/20260409_0003_notifications.py
"""notification history for phase6

Revision ID: 20260409_0003
Revises: 20260408_0002
Create Date: 2026-04-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260409_0003"
down_revision: str | None = "20260408_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    if "notification_events" not in existing:
        op.create_table(
            "notification_events",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("rule_id", sa.Integer(), nullable=False),
            sa.Column("sku", sa.String(length=64), nullable=False),
            sa.Column("rule_type", sa.String(length=32), nullable=False),
            sa.Column("threshold", sa.Float(), nullable=False),
            sa.Column("trigger_price", sa.Float(), nullable=False),
            sa.Column("dedupe_key", sa.String(length=255), nullable=False),
            sa.Column("channel", sa.String(length=32), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("message", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    index_names = {index["name"] for index in inspector.get_indexes("notification_events")}
    sku_index = op.f("ix_notification_events_sku")
    rule_index = op.f("ix_notification_events_rule_id")
    dedupe_index = op.f("ix_notification_events_dedupe_key")

    if sku_index not in index_names:
        op.create_index(sku_index, "notification_events", ["sku"], unique=False)
    if rule_index not in index_names:
        op.create_index(rule_index, "notification_events", ["rule_id"], unique=False)
    if dedupe_index not in index_names:
        op.create_index(dedupe_index, "notification_events", ["dedupe_key"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    if "notification_events" in existing:
        index_names = {index["name"] for index in inspector.get_indexes("notification_events")}
        if op.f("ix_notification_events_dedupe_key") in index_names:
            op.drop_index(op.f("ix_notification_events_dedupe_key"), table_name="notification_events")
        if op.f("ix_notification_events_rule_id") in index_names:
            op.drop_index(op.f("ix_notification_events_rule_id"), table_name="notification_events")
        if op.f("ix_notification_events_sku") in index_names:
            op.drop_index(op.f("ix_notification_events_sku"), table_name="notification_events")
        op.drop_table("notification_events")
