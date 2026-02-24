"""Initial patrol tables

Revision ID: 001_initial_patrols
Revises: 
Create Date: 2025-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_patrols'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create patrols table
    op.create_table(
        'patrols',
        sa.Column('patrol_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('building', sa.String(1), nullable=False),
        sa.Column('entrance', sa.SmallInteger(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='in_progress'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("building IN ('8', '9')", name='ck_patrols_building'),
        sa.CheckConstraint('entrance BETWEEN 1 AND 4', name='ck_patrols_entrance'),
        sa.CheckConstraint("status IN ('in_progress', 'completed')", name='ck_patrols_status'),
        sa.UniqueConstraint('date', 'building', 'entrance', name='uq_patrols_date_building_entrance'),
    )
    
    # Create indexes for patrols
    op.create_index('idx_patrols_date', 'patrols', ['date'])
    op.create_index('idx_patrols_building_entrance', 'patrols', ['building', 'entrance'])
    op.create_index('idx_patrols_status', 'patrols', ['status'])
    
    # Create patrol_entries table
    op.create_table(
        'patrol_entries',
        sa.Column('patrol_entry_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('patrol_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('patrols.patrol_id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('room', sa.String(10), nullable=False),
        sa.Column('is_present', sa.Boolean(), nullable=True),
        sa.Column('absence_reason', sa.Text(), nullable=True),
        sa.Column('checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('patrol_id', 'user_id', name='uq_patrol_entries_patrol_user'),
    )
    
    # Create indexes for patrol_entries
    op.create_index('idx_patrol_entries_patrol_id', 'patrol_entries', ['patrol_id'])
    op.create_index('idx_patrol_entries_user_id', 'patrol_entries', ['user_id'])


def downgrade() -> None:
    op.drop_index('idx_patrol_entries_user_id', table_name='patrol_entries')
    op.drop_index('idx_patrol_entries_patrol_id', table_name='patrol_entries')
    op.drop_table('patrol_entries')
    
    op.drop_index('idx_patrols_status', table_name='patrols')
    op.drop_index('idx_patrols_building_entrance', table_name='patrols')
    op.drop_index('idx_patrols_date', table_name='patrols')
    op.drop_table('patrols')
