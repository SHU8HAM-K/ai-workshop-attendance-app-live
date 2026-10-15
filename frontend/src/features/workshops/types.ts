export type AttendanceStatus = "present" | "absent" | "unmarked";
export interface Student { id: string; student_id: string; name: string; email?: string; institution: string; status?: AttendanceStatus }
export interface Session { id: string; title: string; session_date?: string; starts_at: string; ends_at: string; location: string }
export interface Workshop { id: string; title: string; description: string; topic: string; facilitator_name: string; facilitator_email: string; location: string; starts_on: string; ends_on: string; status: "upcoming" | "active" | "archived"; student_count: number; session_count: number; students?: Student[]; sessions?: Session[] }
export interface AttendanceRecord { student_id: string; student_name: string; student_email: string; status: AttendanceStatus; minutes_attended: number | null }
export interface AttendanceSheet { workshop_id: string; session_id: string; records: AttendanceRecord[] }
export interface StudentCreate { name: string; email: string; student_id: string; institution: string; workshop_id: string }
export interface WorkshopCreate { name: string; description: string; starts_on: string; ends_on: string }
export interface SessionCreate { title: string; session_date: string; starts_at: string; ends_at: string; location: string }
