import { useEffect, useMemo, useState } from "react";
import { Download, Save } from "lucide-react";
import { useAttendance, useSaveAttendance } from "./hooks";
import type { AttendanceRecord, AttendanceStatus, Session, Workshop } from "./types";

function csvCell(value: string | number | null) {
  const text = value === null ? "" : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

function downloadCsv(workshop: Workshop, session: Session, rows: AttendanceRecord[]) {
  const lines = [
    ["Workshop", "Session", "Student", "Email", "Status", "Minutes attended"],
    ...rows.map((row) => [workshop.title, session.title, row.student_name, row.student_email, row.status, row.minutes_attended]),
  ].map((row) => row.map(csvCell).join(","));
  const url = URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url; link.download = `${workshop.title}-${session.title}-attendance.csv`.replaceAll(/[^a-z0-9.-]+/gi, "-").toLowerCase(); link.click();
  URL.revokeObjectURL(url);
}

export function AttendanceRegister({ workshop }: { workshop: Workshop }) {
  const sessions = workshop.sessions ?? [];
  const [sessionId, setSessionId] = useState(sessions[0]?.id ?? "");
  const query = useAttendance(workshop.id, sessionId);
  const save = useSaveAttendance(workshop.id);
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  useEffect(() => { if (query.data) setRecords(query.data.records); }, [query.data]);
  useEffect(() => { if (!sessions.some((item) => item.id === sessionId)) setSessionId(sessions[0]?.id ?? ""); }, [sessionId, sessions]);
  const totals = useMemo(() => ({ present: records.filter((r) => r.status === "present").length, absent: records.filter((r) => r.status === "absent").length, unmarked: records.filter((r) => r.status === "unmarked").length }), [records]);
  const session = sessions.find((item) => item.id === sessionId);
  function update(studentId: string, status: AttendanceStatus, minutes?: number | null) {
    setRecords((current) => current.map((row) => row.student_id === studentId ? { ...row, status, minutes_attended: status === "present" ? (minutes ?? row.minutes_attended ?? 0) : null } : row));
  }
  if (sessions.length === 0) return <div className="empty-feature"><h3>No sessions yet</h3><p>Add a session before taking attendance.</p></div>;
  return <div className="attendance-register"><div className="attendance-toolbar"><label>Session<select aria-label="Attendance session" value={sessionId} onChange={(event) => setSessionId(event.target.value)}>{sessions.map((item) => <option value={item.id} key={item.id}>{item.title}</option>)}</select></label><div>{session && records.length > 0 && <button className="button secondary" onClick={() => downloadCsv(workshop, session, records)}><Download/> Export CSV</button>}<button className="button primary" disabled={!query.data || save.isPending} onClick={() => save.mutate({ workshop_id: workshop.id, session_id: sessionId, records })}><Save/> {save.isPending ? "Saving..." : "Save attendance"}</button></div></div>{query.isPending && <p>Loading attendance...</p>}{query.isError && <div className="inline-error">Could not load attendance.<button onClick={() => void query.refetch()}>Retry</button></div>}{query.data && <><div className="attendance-totals"><span><b>{totals.present}</b> Present</span><span><b>{totals.absent}</b> Absent</span><span><b>{totals.unmarked}</b> Unmarked</span></div><div className="attendance-table"><div className="attendance-head"><span>Student</span><span>Status</span><span>Minutes</span></div>{records.map((row) => <div className="attendance-row" key={row.student_id}><span><strong>{row.student_name}</strong><small>{row.student_email || "No email"}</small></span><span className="status-options">{(["present", "absent", "unmarked"] as const).map((status) => <button type="button" className={row.status === status ? `selected ${status}` : ""} aria-pressed={row.status === status} onClick={() => update(row.student_id, status)} key={status}>{status}</button>)}</span><input aria-label={`Minutes attended for ${row.student_name}`} type="number" min="0" disabled={row.status !== "present"} value={row.minutes_attended ?? ""} onChange={(event) => update(row.student_id, "present", Number(event.target.value))}/></div>)}{records.length === 0 && <p className="empty-row">No students are enrolled in this workshop.</p>}</div>{save.isSuccess && <p className="save-success" role="status">Attendance saved.</p>}{save.isError && <p className="form-error" role="alert">Attendance could not be saved. Please try again.</p>}</>}</div>;
}
