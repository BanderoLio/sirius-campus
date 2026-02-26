"""Initial coworkings and coworking_bookings tables

Revision ID: 001
Revises:
Create Date: 2026-02-26

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "coworkings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("building", sa.Integer(), nullable=False),
        sa.Column("entrance", sa.Integer(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("number"),
    )

    op.create_table(
        "coworking_bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("coworking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("taken_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("returned_back", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'created'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["coworking_id"], ["coworkings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_coworking_bookings_student_id",
        "coworking_bookings",
        ["student_id"],
        unique=False,
    )
    op.create_index(
        "ix_coworking_bookings_coworking_id",
        "coworking_bookings",
        ["coworking_id"],
        unique=False,
    )
    op.create_index(
        "ix_coworking_bookings_status",
        "coworking_bookings",
        ["status"],
        unique=False,
    )

    op.execute(
        """
        INSERT INTO coworkings (id, name, building, entrance, number, available) VALUES
        (gen_random_uuid(), 'Айлант', 8, 1, 5142, true),
        (gen_random_uuid(), 'Магнолия', 8, 2, 5261, true),
        (gen_random_uuid(), 'Гранат', 8, 2, 5367, true),
        (gen_random_uuid(), 'Псоу', 9, 1, 6103, true);
        """
    )


def downgrade() -> None:
    op.drop_index("ix_coworking_bookings_status", table_name="coworking_bookings")
    op.drop_index("ix_coworking_bookings_coworking_id", table_name="coworking_bookings")
    op.drop_index("ix_coworking_bookings_student_id", table_name="coworking_bookings")
    op.drop_table("coworking_bookings")
    op.drop_table("coworkings")
