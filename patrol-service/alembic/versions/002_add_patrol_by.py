"""Add patrol_by field to patrols table, change entrance to string

Revision ID: 002_add_patrol_by
Revises: 001_initial_patrols
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_patrol_by'
down_revision: Union[str, None] = '001_initial_patrols'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change entrance from SMALLINT to VARCHAR(10)
    op.alter_column('patrols', 'entrance',
                   existing_type=sa.SmallInteger(),
                   type_=sa.String(10),
                   existing_nullable=False)
    
    # Add patrol_by column as UUID
    op.add_column(
        'patrols',
        sa.Column(
            'patrol_by',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text('gen_random_uuid()'),
            comment='UUID пользователя, выполняющего обход (студент-обходной или дежурный администратор)'
        )
    )
    
    # Add index on patrol_by for faster lookups
    op.create_index(
        'idx_patrols_patrol_by',
        'patrols',
        ['patrol_by'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('idx_patrols_patrol_by', table_name='patrols')
    op.drop_column('patrols', 'patrol_by')
    op.alter_column('patrols', 'entrance',
                   existing_type=sa.String(10),
                   type_=sa.SmallInteger(),
                   existing_nullable=False)
