from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel, Field

from myapp.domain.attendance import (
    AttendanceRecord,
    AttendanceStatus,
    Student,
    Workshop,
    WorkshopSession,
)
from myapp.entrypoints.api.schemas.common import UtcDatetime


class WorkshopCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = ""
    starts_on: date
    ends_on: date


class WorkshopResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    topic: str
    facilitator_name: str
    facilitator_email: str
    location: str
    status: str
    starts_on: date
    ends_on: date
    student_count: int = 0
    session_count: int = 0

    @classmethod
    def of(cls, w: Workshop, student_count: int = 0, session_count: int = 0) -> WorkshopResponse:
        return cls(
            id=w.id,
            title=w.name,
            description=w.description,
            topic=w.topic or w.description,
            facilitator_name=w.facilitator_name,
            facilitator_email=w.facilitator_email,
            location=w.location,
            status=w.status,
            starts_on=w.starts_on,
            ends_on=w.ends_on,
            student_count=student_count,
            session_count=session_count,
        )


class StudentCreate(BaseModel):
    workshop_id: uuid.UUID
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=320)
    student_id: str = ""
    institution: str = ""


class StudentResponse(BaseModel):
    id: uuid.UUID
    workshop_id: uuid.UUID
    name: str
    email: str
    student_id: str
    institution: str

    @classmethod
    def of(cls, s: Student) -> StudentResponse:
        return cls(
            id=s.id,
            workshop_id=s.workshop_id,
            name=s.name,
            email=s.email,
            student_id=s.student_id,
            institution=s.institution,
        )


class SessionCreate(BaseModel):
    title: str
    session_date: date
    starts_at: UtcDatetime
    ends_at: UtcDatetime
    location: str = ""


class SessionResponse(BaseModel):
    id: uuid.UUID
    workshop_id: uuid.UUID
    title: str
    session_date: date
    starts_at: UtcDatetime
    ends_at: UtcDatetime
    location: str

    @classmethod
    def of(cls, s: WorkshopSession) -> SessionResponse:
        return cls(
            id=s.id,
            workshop_id=s.workshop_id,
            title=s.title,
            session_date=s.session_date,
            starts_at=s.starts_at,
            ends_at=s.ends_at,
            location=s.location,
        )


class WorkshopDetail(WorkshopResponse):
    students: list[StudentResponse]
    sessions: list[SessionResponse]


class AttendanceUpdate(BaseModel):
    student_id: uuid.UUID
    status: AttendanceStatus
    minutes_attended: int | None = Field(default=None, ge=0)


class AttendanceBatch(BaseModel):
    records: list[AttendanceUpdate]


class AttendanceResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    student_email: str
    status: AttendanceStatus
    minutes_attended: int | None


class AttendanceSheet(BaseModel):
    workshop_id: uuid.UUID
    session_id: uuid.UUID
    records: list[AttendanceResponse]


class AttendanceRecordResponse(BaseModel):
    id: uuid.UUID
    workshop_id: uuid.UUID
    session_id: uuid.UUID
    student_id: uuid.UUID
    status: AttendanceStatus
    minutes_spent: int | None

    @classmethod
    def of(cls, r: AttendanceRecord) -> AttendanceRecordResponse:
        return cls(
            id=r.id,
            workshop_id=r.workshop_id,
            session_id=r.session_id,
            student_id=r.student_id,
            status=r.status,
            minutes_spent=r.minutes_spent,
        )
