"""In-memory repositories for service tests.

These are **fakes**, not mocks: real working implementations of the port, backed
by a dict instead of Postgres. A test asserts on the state they end up in
(``uow.notes._notes``), never on which methods were called. That distinction is
why service tests here don't break every time you refactor a service's internals.

Rule: a fake must obey the same contract as the real adapter. If
``SqlAlchemyNoteRepository.list()`` is newest-first, so is this one — otherwise
green service tests will hide a bug that only shows up in production.
"""

from __future__ import annotations

import uuid
from builtins import list as builtin_list

from myapp.domain.attendance import AttendanceRecord, Student, Workshop, WorkshopSession
from myapp.domain.note import Note
from myapp.domain.user import Identity, User
from myapp.ports.repositories import NoteRepository, UserRepository, WorkshopRepository


class FakeNoteRepository(NoteRepository):
    def __init__(self) -> None:
        self._notes: dict[uuid.UUID, Note] = {}

    async def add(self, note: Note) -> None:
        self._notes[note.id] = note

    async def get(self, note_id: uuid.UUID) -> Note | None:
        return self._notes.get(note_id)

    async def list(self, *, include_archived: bool = False) -> list[Note]:
        notes = list(self._notes.values())
        if not include_archived:
            notes = [n for n in notes if not n.is_archived]
        return sorted(notes, key=lambda n: n.created_at, reverse=True)

    async def delete(self, note_id: uuid.UUID) -> None:
        self._notes.pop(note_id, None)


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.items: dict[uuid.UUID, User] = {}
        self.identities: dict[tuple[str, str], uuid.UUID] = {}

    async def add(self, user: User) -> None:
        self.items[user.id] = user

    async def get(self, user_id: uuid.UUID) -> User | None:
        return self.items.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        matches = [u for u in self.items.values() if u.email.lower() == email.lower()]
        return min(matches, key=lambda u: u.created_at, default=None)

    async def get_by_identity(self, provider: str, subject: str) -> User | None:
        user_id = self.identities.get((provider, subject))
        return self.items.get(user_id) if user_id else None

    async def link(self, identity: Identity) -> None:
        self.identities[(identity.provider, identity.subject)] = identity.user_id


class FakeWorkshopRepository(WorkshopRepository):
    def __init__(self) -> None:
        self.workshops: dict[uuid.UUID, Workshop] = {}
        self.students: dict[uuid.UUID, Student] = {}
        self.sessions: dict[uuid.UUID, WorkshopSession] = {}
        self.records: dict[tuple[uuid.UUID, uuid.UUID], AttendanceRecord] = {}

    async def add(self, workshop: Workshop) -> None:
        self.workshops[workshop.id] = workshop

    async def get(self, workshop_id: uuid.UUID) -> Workshop | None:
        return self.workshops.get(workshop_id)

    async def list(self) -> builtin_list[Workshop]:
        return sorted(self.workshops.values(), key=lambda w: w.starts_on, reverse=True)

    async def related_counts(self) -> dict[uuid.UUID, tuple[int, int]]:
        return {
            workshop_id: (
                sum(student.workshop_id == workshop_id for student in self.students.values()),
                sum(session.workshop_id == workshop_id for session in self.sessions.values()),
            )
            for workshop_id in self.workshops
        }

    async def add_student(self, student: Student) -> None:
        self.students[student.id] = student

    async def list_students(self, workshop_id: uuid.UUID) -> builtin_list[Student]:
        return sorted(
            (s for s in self.students.values() if s.workshop_id == workshop_id),
            key=lambda s: s.name,
        )

    async def add_session(self, session: WorkshopSession) -> None:
        self.sessions[session.id] = session

    async def list_sessions(self, workshop_id: uuid.UUID) -> builtin_list[WorkshopSession]:
        return sorted(
            (s for s in self.sessions.values() if s.workshop_id == workshop_id),
            key=lambda s: s.starts_at,
        )

    async def get_session(self, session_id: uuid.UUID) -> WorkshopSession | None:
        return self.sessions.get(session_id)

    async def get_attendance(
        self, workshop_id: uuid.UUID, session_id: uuid.UUID
    ) -> builtin_list[AttendanceRecord]:
        return [
            r
            for r in self.records.values()
            if r.workshop_id == workshop_id and r.session_id == session_id
        ]

    async def get_record(
        self, session_id: uuid.UUID, student_id: uuid.UUID
    ) -> AttendanceRecord | None:
        return self.records.get((session_id, student_id))

    async def add_record(self, record: AttendanceRecord) -> None:
        self.records[(record.session_id, record.student_id)] = record
