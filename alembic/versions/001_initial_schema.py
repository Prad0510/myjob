"""initial_schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-11-05 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create 'jobs' table
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_job_id", sa.Text(), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("company", sa.Text(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("skills", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("experience_required", sa.Text(), nullable=True),
        sa.Column("employment_type", sa.Text(), nullable=True),
        sa.Column("application_method", sa.Text(), nullable=True),
        sa.Column("application_url", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("source_type", sa.Text(), nullable=True),
        sa.Column("fingerprint", sa.Text(), nullable=True),
        sa.Column("source_company", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), server_default="active", nullable=True),
        sa.Column("missed_runs", sa.Integer(), server_default="0", nullable=True),
        sa.Column("last_seen_at", sa.TIMESTAMP(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column("closed_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_jobs_source_source_job_id", "jobs", ["source", "source_job_id"])
    op.create_index("idx_jobs_fingerprint", "jobs", ["fingerprint"])
    op.create_index("idx_jobs_lifecycle", "jobs", ["source", "source_company", "status"])
    op.create_index("idx_jobs_created_at", "jobs", ["created_at"])

    # 2. Create 'collection_runs' table
    op.create_table(
        "collection_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("source_company", sa.Text(), nullable=True),
        sa.Column("started_at", sa.TIMESTAMP(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column("finished_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("jobs_found", sa.Integer(), server_default="0", nullable=True),
        sa.Column("success", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_collection_runs_started_at", "collection_runs", ["started_at"])

    # 3. Create 'job_matches' table
    op.create_table(
        "job_matches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("match_score", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("matched_skills", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("missing_skills", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("role_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("skill_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("experience_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("semantic_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("application_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id", name="uq_job_matches_job_id"),
    )

    op.create_index("idx_job_matches_score", "job_matches", ["match_score"])


def downgrade() -> None:
    op.drop_index("idx_job_matches_score", table_name="job_matches")
    op.drop_table("job_matches")

    op.drop_index("idx_collection_runs_started_at", table_name="collection_runs")
    op.drop_table("collection_runs")

    op.drop_index("idx_jobs_created_at", table_name="jobs")
    op.drop_index("idx_jobs_lifecycle", table_name="jobs")
    op.drop_index("idx_jobs_fingerprint", table_name="jobs")
    op.drop_index("idx_jobs_source_source_job_id", table_name="jobs")
    op.drop_table("jobs")

