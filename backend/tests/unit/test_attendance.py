import uuid
from datetime import UTC, date, datetime, timedelta

import pytest

from myapp.domain.attendance import (
    AttendanceRecord,
    AttendanceStatus,
    InvalidAttendance,
    Student,
    WorkshopSession,
)


def test_student_normalizes_email() -> None:
    student = Student.create(uuid.uuid4(), " Ada ", " ADA@EXAMPLE.COM ", datetime.now(UTC))
    assert (student.name, student.email) == ("Ada", "ada@example.com")


def test_negative_time_is_rejected() -> None:
    record = AttendanceRecord(
        uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), AttendanceStatus.UNMARKED, datetime.now(UTC)
    )
    with pytest.raises(InvalidAttendance):
        record.mark(AttendanceStatus.PRESENT, -1, datetime.now(UTC))


def test_non_present_status_clears_time_spent() -> None:
    record = AttendanceRecord(
        uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), AttendanceStatus.PRESENT, datetime.now(UTC), 45
    )
    record.mark(AttendanceStatus.ABSENT, 45, datetime.now(UTC))
    assert record.minutes_spent is None


def test_session_rejects_an_invalid_time_range() -> None:
    now = datetime.now(UTC)
    with pytest.raises(InvalidAttendance):
        WorkshopSession.create(uuid.uuid4(), "Day 1", date.today(), now, now - timedelta(minutes=1))
