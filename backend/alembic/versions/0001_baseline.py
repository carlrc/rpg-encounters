"""Baseline revision for pre-Alembic environments.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-02-23 16:50:00
"""

from __future__ import annotations

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing databases should be stamped to this revision.
    # Intentionally no-op to avoid replaying DDL on live schemas.
    pass


def downgrade() -> None:
    pass
