from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from myapp.bootstrap import get_attendance_service
from myapp.entrypoints.api.schemas.attendance import (
    AttendanceBatch,
    AttendanceResponse,
    AttendanceSheet,
    SessionCreate,
    SessionResponse,
    StudentCreate,
    StudentResponse,
    WorkshopCreate,
    WorkshopDetail,
    WorkshopResponse,
)
from myapp.services.attendance import AttendanceService

router = APIRouter(tags=["attendance"])


@router.get("/workshops", response_model=list[WorkshopResponse])
async def list_workshops(
    service: AttendanceService = Depends(get_attendance_service),
) -> list[WorkshopResponse]:
    return [
        WorkshopResponse.of(workshop, student_count, session_count)
        for workshop, student_count, session_count in await service.list_workshop_summaries()
    ]


@router.post("/workshops", response_model=WorkshopResponse, status_code=status.HTTP_201_CREATED)
async def create_workshop(
    payload: WorkshopCreate, service: AttendanceService = Depends(get_attendance_service)
) -> WorkshopResponse:
    return WorkshopResponse.of(
        await service.create_workshop(
            payload.name, payload.description, payload.starts_on, payload.ends_on
        )
    )


@router.get("/workshops/{workshop_id}", response_model=WorkshopDetail)
async def workshop_detail(
    workshop_id: uuid.UUID, service: AttendanceService = Depends(get_attendance_service)
) -> WorkshopDetail:
    w, students, sessions = await service.detail(workshop_id)
    return WorkshopDetail(
        **WorkshopResponse.of(w, len(students), len(sessions)).model_dump(),
        students=[StudentResponse.of(s) for s in students],
        sessions=[SessionResponse.of(s) for s in sessions],
    )


@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def add_student(
    payload: StudentCreate, service: AttendanceService = Depends(get_attendance_service)
) -> StudentResponse:
    return StudentResponse.of(
        await service.add_student(
            payload.workshop_id,
            payload.name,
            payload.email,
            payload.student_id,
            payload.institution,
        )
    )


@router.post(
    "/workshops/{workshop_id}/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_session(
    workshop_id: uuid.UUID,
    payload: SessionCreate,
    service: AttendanceService = Depends(get_attendance_service),
) -> SessionResponse:
    return SessionResponse.of(
        await service.add_session(
            workshop_id,
            payload.title,
            payload.session_date,
            payload.starts_at,
            payload.ends_at,
            payload.location,
        )
    )


@router.get("/workshops/{workshop_id}/attendance", response_model=AttendanceSheet)
async def get_attendance(
    workshop_id: uuid.UUID,
    session_id: uuid.UUID = Query(),
    service: AttendanceService = Depends(get_attendance_service),
) -> AttendanceSheet:
    students, records = await service.attendance(workshop_id, session_id)
    by_student = {r.student_id: r for r in records}
    return AttendanceSheet(
        workshop_id=workshop_id,
        session_id=session_id,
        records=[
            AttendanceResponse(
                student_id=s.id,
                student_name=s.name,
                student_email=s.email,
                status=by_student[s.id].status if s.id in by_student else "unmarked",
                minutes_attended=by_student[s.id].minutes_spent if s.id in by_student else None,
            )
            for s in students
        ],
    )


@router.put("/workshops/{workshop_id}/attendance/{session_id}", response_model=AttendanceSheet)
async def mark_attendance(
    workshop_id: uuid.UUID,
    session_id: uuid.UUID,
    payload: AttendanceBatch,
    service: AttendanceService = Depends(get_attendance_service),
) -> AttendanceSheet:
    await service.mark(
        workshop_id,
        session_id,
        [(r.student_id, r.status, r.minutes_attended) for r in payload.records],
    )
    students, records = await service.attendance(workshop_id, session_id)
    by_student = {r.student_id: r for r in records}
    return AttendanceSheet(
        workshop_id=workshop_id,
        session_id=session_id,
        records=[
            AttendanceResponse(
                student_id=s.id,
                student_name=s.name,
                student_email=s.email,
                status=by_student[s.id].status if s.id in by_student else "unmarked",
                minutes_attended=by_student[s.id].minutes_spent if s.id in by_student else None,
            )
            for s in students
        ],
    )
