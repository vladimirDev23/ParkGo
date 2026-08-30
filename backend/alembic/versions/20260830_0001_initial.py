"""Initial ParkGo schema with PostGIS.

Revision ID: 20260830_0001
Revises:
"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260830_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.create_table(
        "users",
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100)),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table(
        "parking_zones",
        sa.Column("external_id", sa.String(100), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("zone_number", sa.String(30), nullable=False),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=False),
        sa.Column(
            "geometry",
            geoalchemy2.Geometry("POINT", srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column("address", sa.String(255), nullable=False),
        sa.Column("hourly_rate", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("active_from", sa.Time()),
        sa.Column("active_until", sa.Time()),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "external_id", name="uq_zone_provider_external_id"),
    )
    op.create_index(
        "ix_parking_zones_geometry_gist", "parking_zones", ["geometry"], postgresql_using="gist"
    )
    op.create_index("ix_parking_zones_provider", "parking_zones", ["provider"])
    op.create_index("ix_parking_zones_zone_number", "parking_zones", ["zone_number"])
    op.create_index("ix_parking_zones_active", "parking_zones", ["is_active"])
    op.create_table(
        "vehicles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("plate_number", sa.String(20), nullable=False),
        sa.Column("region_code", sa.String(10), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("brand", sa.String(80)),
        sa.Column("model", sa.String(80)),
        sa.Column("color", sa.String(50)),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "plate_number", "region_code", name="uq_vehicle_plate"),
    )
    op.create_index("ix_vehicles_user_id", "vehicles", ["user_id"])
    op.create_index(
        "uq_vehicle_one_default_per_user",
        "vehicles",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_default IS true"),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("jti", sa.String(64), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
        sa.Column("replaced_by_jti", sa.String(64)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("jti"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"])
    op.create_table(
        "parking_sessions",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("vehicle_id", sa.Uuid(), nullable=False),
        sa.Column("parking_zone_id", sa.Uuid(), nullable=False),
        sa.Column("provider_session_id", sa.String(150)),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("calculated_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("payment_status", sa.String(20), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["parking_zone_id"], ["parking_zones.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_session_id"),
    )
    op.create_index("ix_sessions_user_started", "parking_sessions", ["user_id", "started_at"])
    op.create_index(
        "uq_one_active_session_per_user",
        "parking_sessions",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )
    op.create_index("ix_parking_sessions_status", "parking_sessions", ["status"])
    op.create_index("ix_parking_sessions_vehicle_id", "parking_sessions", ["vehicle_id"])
    op.create_index("ix_parking_sessions_parking_zone_id", "parking_sessions", ["parking_zone_id"])
    op.create_table(
        "payments",
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("external_payment_id", sa.String(150), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["parking_sessions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_payment_id"),
        sa.UniqueConstraint("session_id"),
    )
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_table(
        "notification_devices",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("push_token", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform", "push_token", name="uq_notification_platform_token"),
    )
    op.create_index("ix_notification_devices_user_id", "notification_devices", ["user_id"])


def downgrade() -> None:
    op.drop_table("notification_devices")
    op.drop_table("payments")
    op.drop_table("parking_sessions")
    op.drop_table("refresh_tokens")
    op.drop_table("vehicles")
    op.drop_index("ix_parking_zones_geometry_gist", table_name="parking_zones")
    op.drop_table("parking_zones")
    op.drop_table("users")
