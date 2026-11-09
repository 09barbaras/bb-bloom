"""baseline

Revision ID: 2223acd287ba
Revises:
Create Date: 2026-11-09 12:56:42.904592

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "2223acd287ba"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
