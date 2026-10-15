import { api } from "@/lib/api";
import type { AttendanceSheet, Session, SessionCreate, Student, StudentCreate, Workshop, WorkshopCreate } from "./types";
export const workshopKeys = { all: ["workshops"] as const, lists: () => ["workshops", "list"] as const, detail: (id: string) => ["workshops", "detail", id] as const, attendance: (id: string, sessionId: string) => ["workshops", "detail", id, "attendance", sessionId] as const };
export const studentKeys = { all: ["students"] as const };
export const workshopsApi = {
  list: () => api.get<Workshop[]>("/workshops"), detail: (id: string) => api.get<Workshop>(`/workshops/${id}`),
  create: (payload: WorkshopCreate) => api.post<Workshop>("/workshops", payload),
  createStudent: (payload: StudentCreate) => api.post<Student>("/students", payload),
  createSession: (id: string, payload: SessionCreate) => api.post<Session>(`/workshops/${id}/sessions`, payload),
  attendance: (id: string, sessionId: string) => api.get<AttendanceSheet>(`/workshops/${id}/attendance?session_id=${encodeURIComponent(sessionId)}`),
  saveAttendance: (id: string, sheet: AttendanceSheet) => api.put<AttendanceSheet>(`/workshops/${id}/attendance/${sheet.session_id}`, { records: sheet.records }),
};
