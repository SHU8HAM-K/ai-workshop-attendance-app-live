from datetime import UTC, date, datetime, timedelta

import pytest

from myapp.domain.attendance import AttendanceStatus, InvalidAttendance
from myapp.services.attendance import AttendanceService


@pytest.mark.asyncio
async def test_attendance_use_case(uow) -> None:
    service = AttendanceService(uow)
    workshop = await service.create_workshop("AI", "", date.today(), date.today())
    student = await service.add_student(workshop.id, "Ada", "ada@example.com")
    now = datetime.now(UTC)
    session = await service.add_session(
        workshop.id, "Day 1", date.today(), now, now + timedelta(hours=1)
    )
    records = await service.mark(
        workshop.id, session.id, [(student.id, AttendanceStatus.PRESENT, 55)]
    )
    assert records[0].minutes_spent == 55
    summaries = await service.list_workshop_summaries()
    assert summaries == [(workshop, 1, 1)]

    with pytest.raises(InvalidAttendance, match="session duration"):
        await service.mark(workshop.id, session.id, [(student.id, AttendanceStatus.PRESENT, 61)])
