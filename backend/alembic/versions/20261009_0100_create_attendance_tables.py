"""create attendance tables

Revision ID: 20261009_0100
Revises: 0002_users
"""
from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op
revision: str = "20261009_0100"
down_revision: str | None = "0002_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("workshops", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("name", sa.String(200), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("starts_on", sa.Date(), nullable=False), sa.Column("ends_on", sa.Date(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("topic", sa.String(200), nullable=False, server_default=""), sa.Column("facilitator_name", sa.String(200), nullable=False, server_default=""), sa.Column("facilitator_email", sa.String(320), nullable=False, server_default=""), sa.Column("location", sa.String(300), nullable=False, server_default=""), sa.Column("status", sa.String(30), nullable=False, server_default="upcoming"))
    op.create_index("ix_workshops_starts_on", "workshops", ["starts_on"])
    op.create_table("students", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("workshop_id", sa.Uuid(), sa.ForeignKey("workshops.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(200), nullable=False), sa.Column("email", sa.String(320), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("student_id", sa.String(100), nullable=False, server_default=""), sa.Column("institution", sa.String(300), nullable=False, server_default=""), sa.UniqueConstraint("workshop_id", "email", name="uq_students_workshop_email"))
    op.create_index("ix_students_workshop", "students", ["workshop_id"])
    op.create_table("workshop_sessions", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("workshop_id", sa.Uuid(), sa.ForeignKey("workshops.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("session_date", sa.Date(), nullable=False), sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False), sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False), sa.Column("location", sa.String(300), nullable=False, server_default=""))
    op.create_index("ix_sessions_workshop_date", "workshop_sessions", ["workshop_id", "session_date"])
    op.create_table("attendance_records", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("workshop_id", sa.Uuid(), sa.ForeignKey("workshops.id", ondelete="CASCADE"), nullable=False), sa.Column("session_id", sa.Uuid(), sa.ForeignKey("workshop_sessions.id", ondelete="CASCADE"), nullable=False), sa.Column("student_id", sa.Uuid(), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("minutes_spent", sa.Integer(), nullable=True), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("session_id", "student_id", name="uq_attendance_session_student"))
    op.create_index("ix_attendance_workshop_session", "attendance_records", ["workshop_id", "session_id"])

def downgrade() -> None:
    op.drop_table("attendance_records"); op.drop_table("workshop_sessions"); op.drop_table("students"); op.drop_table("workshops")
