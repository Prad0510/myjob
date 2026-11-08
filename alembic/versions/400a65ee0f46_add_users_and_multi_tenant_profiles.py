"""add_users_and_multi_tenant_profiles

Revision ID: 400a65ee0f46
Revises: 001_initial_schema
Create Date: 2026-11-08 18:27:08.506396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '400a65ee0f46'
down_revision: Union[str, Sequence[str], None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create 'users' table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_chat_id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_username", sa.Text(), nullable=True),
        sa.Column("first_name", sa.Text(), nullable=True),
        sa.Column("last_name", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_chat_id", name="uq_users_telegram_chat_id"),
    )
    op.create_index("idx_users_telegram_chat_id", "users", ["telegram_chat_id"])

    # 2. Create 'candidate_profiles' table
    op.create_table(
        "candidate_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("skills", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("target_roles", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("profile_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("resume_filename", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_candidate_profiles_user_id"),
    )

    # 3. Update 'job_matches' to be multi-tenant (per user)
    # Drop old unique constraint on job_id alone if it exists
    op.drop_constraint("job_matches_job_id_key", "job_matches", type_="unique")
    
    # Add user_id column
    op.add_column("job_matches", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_job_matches_user_id",
        "job_matches",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # Unique constraint per user and job
    op.create_unique_constraint("uq_job_matches_user_job", "job_matches", ["user_id", "job_id"])


def downgrade() -> None:
    op.drop_constraint("uq_job_matches_user_job", "job_matches", type_="unique")
    op.drop_constraint("fk_job_matches_user_id", "job_matches", type_="foreignkey")
    op.drop_column("job_matches", "user_id")
    op.create_unique_constraint("job_matches_job_id_key", "job_matches", ["job_id"])
    op.drop_table("candidate_profiles")
    op.drop_index("idx_users_telegram_chat_id", table_name="users")
    op.drop_table("users")
