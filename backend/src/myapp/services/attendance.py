from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

from myapp.domain.attendance import (
    AttendanceRecord,
    AttendanceStatus,
    InvalidAttendance,
    Student,
    Workshop,
    WorkshopSession,
)
from myapp.domain.exceptions import ConflictError, NotFoundError
from myapp.ports.unit_of_work import UnitOfWork


class WorkshopNotFound(NotFoundError):
    pass


class SessionNotFound(NotFoundError):
    pass


class AttendanceService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def create_workshop(
        self, name: str, description: str, starts_on: date, ends_on: date
    ) -> Workshop:
        async with self._uow as uow:
            item = Workshop.create(name, description, starts_on, ends_on, datetime.now(UTC))
            await uow.workshops.add(item)
            await uow.commit()
            return item

    async def list_workshops(self) -> list[Workshop]:
        async with self._uow as uow:
            return await uow.workshops.list()

    async def list_workshop_summaries(self) -> list[tuple[Workshop, int, int]]:
        async with self._uow as uow:
            workshops = await uow.workshops.list()
            counts = await uow.workshops.related_counts()
            return [(workshop, *counts.get(workshop.id, (0, 0))) for workshop in workshops]

    async def detail(
        self, workshop_id: uuid.UUID
    ) -> tuple[Workshop, list[Student], list[WorkshopSession]]:
        async with self._uow as uow:
            workshop = await uow.workshops.get(workshop_id)
            if workshop is None:
                raise WorkshopNotFound("Workshop not found.")
            return (
                workshop,
                await uow.workshops.list_students(workshop_id),
                await uow.workshops.list_sessions(workshop_id),
            )

    async def add_student(
        self,
        workshop_id: uuid.UUID,
        name: str,
        email: str,
        student_id: str = "",
        institution: str = "",
    ) -> Student:
        async with self._uow as uow:
            if await uow.workshops.get(workshop_id) is None:
                raise WorkshopNotFound("Workshop not found.")
            student = Student.create(
                workshop_id, name, email, datetime.now(UTC), student_id, institution
            )
            if student.email and any(
                s.email == student.email for s in await uow.workshops.list_students(workshop_id)
            ):
                raise ConflictError("Student email already exists in this workshop.")
            await uow.workshops.add_student(student)
            await uow.commit()
            return student

    async def add_session(
        self,
        workshop_id: uuid.UUID,
        title: str,
        session_date: date,
        starts_at: datetime,
        ends_at: datetime,
        location: str = "",
    ) -> WorkshopSession:
        async with self._uow as uow:
            if await uow.workshops.get(workshop_id) is None:
                raise WorkshopNotFound("Workshop not found.")
            item = WorkshopSession.create(
                workshop_id, title, session_date, starts_at, ends_at, location
            )
            await uow.workshops.add_session(item)
            await uow.commit()
            return item

    async def attendance(
        self, workshop_id: uuid.UUID, session_id: uuid.UUID
    ) -> tuple[list[Student], list[AttendanceRecord]]:
        async with self._uow as uow:
            await self._validate_session(uow, workshop_id, session_id)
            return await uow.workshops.list_students(
                workshop_id
            ), await uow.workshops.get_attendance(workshop_id, session_id)

    async def mark(
        self,
        workshop_id: uuid.UUID,
        session_id: uuid.UUID,
        updates: list[tuple[uuid.UUID, AttendanceStatus, int | None]],
    ) -> list[AttendanceRecord]:
        async with self._uow as uow:
            session = await self._validate_session(uow, workshop_id, session_id)
            students = {s.id for s in await uow.workshops.list_students(workshop_id)}
            now = datetime.now(UTC)
            for student_id, status, minutes in updates:
                if student_id not in students:
                    raise NotFoundError("Student not found in this workshop.")
                duration = int((session.ends_at - session.starts_at).total_seconds() // 60)
                if minutes is not None and minutes > duration:
                    raise InvalidAttendance("Time spent cannot exceed the session duration.")
                record = await uow.workshops.get_record(session_id, student_id)
                if record is None:
                    record = AttendanceRecord(workshop_id, session_id, student_id, status, now)
                    await uow.workshops.add_record(record)
                record.mark(status, minutes, now)
            await uow.commit()
            return await uow.workshops.get_attendance(workshop_id, session_id)

    @staticmethod
    async def _validate_session(
        uow: UnitOfWork, workshop_id: uuid.UUID, session_id: uuid.UUID
    ) -> WorkshopSession:
        session = await uow.workshops.get_session(session_id)
        if session is None or session.workshop_id != workshop_id:
            raise SessionNotFound("Session not found in this workshop.")
        return session
