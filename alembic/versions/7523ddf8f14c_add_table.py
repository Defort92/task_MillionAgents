"""add table

Revision ID: 7523ddf8f14c
Revises: 8d4d80d666aa
Create Date: 2024-08-18 23:32:37.040288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7523ddf8f14c'
down_revision: Union[str, None] = '8d4d80d666aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file_metadata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uid', sa.String(), nullable=True),
    sa.Column('original_name', sa.String(), nullable=True),
    sa.Column('size', sa.Integer(), nullable=True),
    sa.Column('content_type', sa.String(), nullable=True),
    sa.Column('path', sa.String(), nullable=True),
    sa.Column('storage_url', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_file_metadata_id'), 'file_metadata', ['id'], unique=False)
    op.create_index(op.f('ix_file_metadata_original_name'), 'file_metadata', ['original_name'], unique=False)
    op.create_index(op.f('ix_file_metadata_uid'), 'file_metadata', ['uid'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_file_metadata_uid'), table_name='file_metadata')
    op.drop_index(op.f('ix_file_metadata_original_name'), table_name='file_metadata')
    op.drop_index(op.f('ix_file_metadata_id'), table_name='file_metadata')
    op.drop_table('file_metadata')
    # ### end Alembic commands ###
