"""add uploaded meeting status

Revision ID: 7e9b73f8bff4
Revises: 47c95ab8d2fd
Create Date: 2026-08-18 14:18:14.404233

"""
from alembic import op


revision: str = '7e9b73f8bff4'
down_revision: str | None = '47c95ab8d2fd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE meetingstatus ADD VALUE 'UPLOADED'"
    )


def downgrade() -> None:
    pass