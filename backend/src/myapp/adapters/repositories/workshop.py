from __future__ import annotations

import uuid
from builtins import list as builtin_list

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from myapp.adapters.orm.tables import attendance_table, session_table, student_table, workshop_table
from myapp.domain.attendance import AttendanceRecord, Student, Workshop, WorkshopSession
from myapp.ports.repositories import WorkshopRepository


class SqlAlchemyWorkshopRepository(WorkshopRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, workshop: Workshop) -> None:
        self._session.add(workshop)

    async def get(self, workshop_id: uuid.UUID) -> Workshop | None:
        return (
            await self._session.execute(select(Workshop).where(workshop_table.c.id == workshop_id))
        ).scalar_one_or_none()

    async def list(self) -> builtin_list[Workshop]:
        return list(
            (
                await self._session.execute(
                    select(Workshop).order_by(workshop_table.c.starts_on.desc())
                )
            ).scalars()
        )

    async def related_counts(self) -> dict[uuid.UUID, tuple[int, int]]:
        student_rows = await self._session.execute(
            select(student_table.c.workshop_id, func.count()).group_by(student_table.c.workshop_id)
        )
        session_rows = await self._session.execute(
            select(session_table.c.workshop_id, func.count()).group_by(session_table.c.workshop_id)
        )
        students: dict[uuid.UUID, int] = {}
        for workshop_id, count in student_rows:
            students[workshop_id] = count
        sessions: dict[uuid.UUID, int] = {}
        for workshop_id, count in session_rows:
            sessions[workshop_id] = count
        return {
            workshop_id: (students.get(workshop_id, 0), sessions.get(workshop_id, 0))
            for workshop_id in students.keys() | sessions.keys()
        }

    async def add_student(self, student: Student) -> None:
        self._session.add(student)

    async def list_students(self, workshop_id: uuid.UUID) -> builtin_list[Student]:
        return list(
            (
                await self._session.execute(
                    select(Student)
                    .where(student_table.c.workshop_id == workshop_id)
                    .order_by(student_table.c.name)
                )
            ).scalars()
        )

    async def add_session(self, session: WorkshopSession) -> None:
        self._session.add(session)

    async def list_sessions(self, workshop_id: uuid.UUID) -> builtin_list[WorkshopSession]:
        return list(
            (
                await self._session.execute(
                    select(WorkshopSession)
                    .where(session_table.c.workshop_id == workshop_id)
                    .order_by(session_table.c.starts_at)
                )
            ).scalars()
        )

    async def get_session(self, session_id: uuid.UUID) -> WorkshopSession | None:
        return (
            await self._session.execute(
                select(WorkshopSession).where(session_table.c.id == session_id)
            )
        ).scalar_one_or_none()

    async def get_attendance(
        self, workshop_id: uuid.UUID, session_id: uuid.UUID
    ) -> builtin_list[AttendanceRecord]:
        stmt = select(AttendanceRecord).where(
            attendance_table.c.workshop_id == workshop_id,
            attendance_table.c.session_id == session_id,
        )
        return list((await self._session.execute(stmt)).scalars())

    async def get_record(
        self, session_id: uuid.UUID, student_id: uuid.UUID
    ) -> AttendanceRecord | None:
        stmt = select(AttendanceRecord).where(
            attendance_table.c.session_id == session_id, attendance_table.c.student_id == student_id
        )
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def add_record(self, record: AttendanceRecord) -> None:
        self._session.add(record)
