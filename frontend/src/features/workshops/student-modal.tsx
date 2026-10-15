import { useState, type FormEvent } from "react";
import { X } from "lucide-react";
import { ApiError } from "@/lib/api";
import { useCreateStudent } from "./hooks";

export function StudentModal({ workshopId, onClose }: { workshopId: string; onClose: () => void }) {
  const create = useCreateStudent();
  const [error, setError] = useState("");
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = new FormData(event.currentTarget);
    create.mutate({ workshop_id: workshopId, name: String(form.get("name")), email: String(form.get("email")), student_id: String(form.get("studentId")), institution: String(form.get("institution")) }, { onSuccess: onClose, onError: (reason) => setError(reason instanceof ApiError && reason.isUserFixable ? reason.detail : "Student could not be added. Please try again.") });
  }
  return <div className="modal-backdrop"><section className="modal" role="dialog" aria-modal="true" aria-labelledby="student-modal-title"><header><div><span className="eyebrow">Student record</span><h2 id="student-modal-title">Add a student</h2></div><button className="icon-button" aria-label="Close" onClick={onClose}><X/></button></header><form onSubmit={submit}><div className="form-grid"><label>Full name<input name="name" required placeholder="e.g. Aarav Singh"/></label><label>Email address<input name="email" type="email" required placeholder="aarav@example.com"/></label><label>Student ID<input name="studentId" required placeholder="SN-2413"/></label><label>Institution<input name="institution" required placeholder="School or institution"/></label></div>{error && <p className="form-error" role="alert">{error}</p>}<footer><button type="button" className="button secondary" onClick={onClose}>Cancel</button><button className="button primary" disabled={create.isPending}>{create.isPending ? "Adding..." : "Add student"}</button></footer></form></section></div>;
}
