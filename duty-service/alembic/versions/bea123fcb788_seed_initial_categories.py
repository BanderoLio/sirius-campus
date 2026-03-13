"""Seed initial categories

Revision ID: bea123fcb788
Revises: bdc78466d903
Create Date: 2026-03-04 06:33:47.992218

"""
from typing import Sequence, Union
from uuid import uuid4
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID


revision: str = 'bea123fcb788'
down_revision: Union[str, None] = 'bdc78466d903'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    duty_categories = table('duty_categories',
        column('id', UUID(as_uuid=True)),
        column('name', sa.String),
        column('created_at', DateTime),
        column('updated_at', DateTime),
    )
    
    now = datetime.utcnow()
    
    op.bulk_insert(duty_categories, [
        {
            'id': uuid4(),
            'name': 'Кухня',
            'created_at': now,
            'updated_at': now,
        },
        {
            'id': uuid4(),
            'name': 'Коворкинг',
            'created_at': now,
            'updated_at': now,
        },
        {
            'id': uuid4(),
            'name': 'Постирочная',
            'created_at': now,
            'updated_at': now,
        },
    ])


def downgrade() -> None:
    op.execute(
        "DELETE FROM duty_categories WHERE name IN ('Кухня', 'Коридор', 'Санузлы')"
    )
