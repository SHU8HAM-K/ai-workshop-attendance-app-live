from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum

from myapp.domain.exceptions import ConflictError, ValidationError


class AttendanceStatus(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    UNMARKED = "unmarked"


class InvalidAttendance(ValidationError):
    pass


class DuplicateStudent(ConflictError):
    pass


@dataclass
class Student:
    workshop_id: uuid.UUID
    name: str
    email: str
    created_at: datetime
    student_id: str = ""
    institution: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    @classmethod
    def create(
        cls,
        workshop_id: uuid.UUID,
        name: str,
        email: str,
        now: datetime,
        student_id: str = "",
        institution: str = "",
    ) -> Student:
        name, email = name.strip(), email.strip().lower()
        if not name or (email and "@" not in email):
            raise InvalidAttendance("Student details are invalid.")
        return cls(
            workshop_id=workshop_id,
            name=name,
            email=email,
            created_at=now,
            student_id=student_id.strip(),
            institution=institution.strip(),
        )


@dataclass
class WorkshopSession:
    workshop_id: uuid.UUID
    title: str
    session_date: date
    starts_at: datetime
    ends_at: datetime
    location: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    @classmethod
    def create(
        cls,
        workshop_id: uuid.UUID,
        title: str,
        session_date: date,
        starts_at: datetime,
        ends_at: datetime,
        location: str = "",
    ) -> WorkshopSession:
        title = title.strip()
        if not title or ends_at <= starts_at:
            raise InvalidAttendance("Session title and times are invalid.")
        return cls(workshop_id, title, session_date, starts_at, ends_at, location.strip())


@dataclass
class AttendanceRecord:
    workshop_id: uuid.UUID
    session_id: uuid.UUID
    student_id: uuid.UUID
    status: AttendanceStatus
    updated_at: datetime
    minutes_spent: int | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def mark(self, status: AttendanceStatus, minutes_spent: int | None, now: datetime) -> None:
        if minutes_spent is not None and minutes_spent < 0:
            raise InvalidAttendance("Time spent cannot be negative.")
        if status is AttendanceStatus.PRESENT and minutes_spent is None:
            raise InvalidAttendance("Time spent is required for present students.")
        if status is not AttendanceStatus.PRESENT:
            minutes_spent = None
        self.status, self.minutes_spent, self.updated_at = status, minutes_spent, now


@dataclass
class Workshop:
    name: str
    description: str
    starts_on: date
    ends_on: date
    created_at: datetime
    topic: str = ""
    facilitator_name: str = ""
    facilitator_email: str = ""
    location: str = ""
    status: str = "upcoming"
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    @classmethod
    def create(
        cls, name: str, description: str, starts_on: date, ends_on: date, now: datetime
    ) -> Workshop:
        name = name.strip()
        if not name or ends_on < starts_on:
            raise InvalidAttendance("Workshop name and date range are invalid.")
        return cls(
            name=name,
            description=description.strip(),
            starts_on=starts_on,
            ends_on=ends_on,
            created_at=now,
        )
