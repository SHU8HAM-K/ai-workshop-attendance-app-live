"""Ports — abstract repository contracts. Imports domain only.

A port is the *shape of the hole*; an adapter is the *plug*. Keeping them in
separate packages makes the abstract surface of the app visible in one place: if
it isn't listed here, no service can depend on it.

One repository per **aggregate root**, not per table. ``NoteRepository`` would
also own a note's comments/attachments if it had them — you would never add a
``CommentRepository`` that hands out comments detached from their note.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from builtins import list as builtin_list

from myapp.domain.attendance import AttendanceRecord, Student, Workshop, WorkshopSession
from myapp.domain.note import Note
from myapp.domain.user import Identity, User


class NoteRepository(ABC):
    """Collection-shaped abstraction over storage. Note the vocabulary: ``add``
    and ``get``, not ``insert`` and ``select`` — a repository pretends to be a
    set of domain objects, and the SQL is an implementation detail of one adapter.
    """

    @abstractmethod
    async def add(self, note: Note) -> None:
        """Put a note in the collection. No commit — the Unit of Work owns that."""

    @abstractmethod
    async def get(self, note_id: uuid.UUID) -> Note | None:
        """The note, or None. Returning None (not raising) keeps the 'does this
        exist?' decision with the caller, which knows what it means."""

    @abstractmethod
    async def list(self, *, include_archived: bool = False) -> list[Note]:
        """Newest first. Filtering lives here rather than in the service so the
        database does the work instead of Python."""

    @abstractmethod
    async def delete(self, note_id: uuid.UUID) -> None:
        """Idempotent: deleting an absent id is not an error."""


class UserRepository(ABC):
    """Users and the provider identities linked to them."""

    @abstractmethod
    async def add(self, user: User) -> None: ...

    @abstractmethod
    async def get(self, user_id: uuid.UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Case-insensitive. The oldest match if several share the address."""

    @abstractmethod
    async def get_by_identity(self, provider: str, subject: str) -> User | None: ...

    @abstractmethod
    async def link(self, identity: Identity) -> None: ...


class WorkshopRepository(ABC):
    @abstractmethod
    async def add(self, workshop: Workshop) -> None: ...
    @abstractmethod
    async def get(self, workshop_id: uuid.UUID) -> Workshop | None: ...
    @abstractmethod
    async def list(self) -> builtin_list[Workshop]: ...
    @abstractmethod
    async def related_counts(self) -> dict[uuid.UUID, tuple[int, int]]: ...
    @abstractmethod
    async def add_student(self, student: Student) -> None: ...
    @abstractmethod
    async def list_students(self, workshop_id: uuid.UUID) -> builtin_list[Student]: ...
    @abstractmethod
    async def add_session(self, session: WorkshopSession) -> None: ...
    @abstractmethod
    async def list_sessions(self, workshop_id: uuid.UUID) -> builtin_list[WorkshopSession]: ...
    @abstractmethod
    async def get_session(self, session_id: uuid.UUID) -> WorkshopSession | None: ...
    @abstractmethod
    async def get_attendance(
        self, workshop_id: uuid.UUID, session_id: uuid.UUID
    ) -> builtin_list[AttendanceRecord]: ...
    @abstractmethod
    async def get_record(
        self, session_id: uuid.UUID, student_id: uuid.UUID
    ) -> AttendanceRecord | None: ...
    @abstractmethod
    async def add_record(self, record: AttendanceRecord) -> None: ...
