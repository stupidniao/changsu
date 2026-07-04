"""Create bills table."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260703_2236"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("direction", sa.String(length=16), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("account", sa.String(length=64), nullable=False),
        sa.Column("merchant", sa.String(length=128), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("trace_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bills_id"), "bills", ["id"], unique=False)
    op.create_index(op.f("ix_bills_trace_id"), "bills", ["trace_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_bills_trace_id"), table_name="bills")
    op.drop_index(op.f("ix_bills_id"), table_name="bills")
    op.drop_table("bills")
