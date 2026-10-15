import { useState, type FormEvent } from "react";
import { X } from "lucide-react";
import { ApiError } from "@/lib/api";
import { useCreateSession, useCreateWorkshop } from "./hooks";

function message(reason: unknown, fallback: string) {
  return reason instanceof ApiError && reason.isUserFixable ? reason.detail : fallback;
}

export function WorkshopModal({ onClose }: { onClose: () => void }) {
  const create = useCreateWorkshop();
  const [error, setError] = useState("");
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    create.mutate({
      name: String(form.get("name")), description: String(form.get("description")),
      starts_on: String(form.get("startsOn")), ends_on: String(form.get("endsOn")),
    }, { onSuccess: onClose, onError: (reason) => setError(message(reason, "Workshop could not be created. Please try again.")) });
  }
  return <div className="modal-backdrop"><section className="modal" role="dialog" aria-modal="true" aria-labelledby="workshop-modal-title"><header><div><span className="eyebrow">Workshop setup</span><h2 id="workshop-modal-title">Create a workshop</h2></div><button type="button" className="icon-button" aria-label="Close" onClick={onClose}><X/></button></header><form onSubmit={submit}><label>Workshop name<input name="name" required maxLength={200} placeholder="e.g. AI Essentials"/></label><label className="form-field">Description<textarea name="description" rows={3} placeholder="What will learners cover?"/></label><div className="form-grid"><label>Start date<input name="startsOn" type="date" required/></label><label>End date<input name="endsOn" type="date" required/></label></div>{error && <p className="form-error" role="alert">{error}</p>}<footer><button type="button" className="button secondary" onClick={onClose}>Cancel</button><button className="button primary" disabled={create.isPending}>{create.isPending ? "Creating..." : "Create workshop"}</button></footer></form></section></div>;
}

export function SessionModal({ workshopId, onClose }: { workshopId: string; onClose: () => void }) {
  const create = useCreateSession(workshopId);
  const [error, setError] = useState("");
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const day = String(form.get("sessionDate"));
    const startsAt = new Date(`${day}T${String(form.get("startsAt"))}`).toISOString();
    const endsAt = new Date(`${day}T${String(form.get("endsAt"))}`).toISOString();
    create.mutate({ title: String(form.get("title")), session_date: day, starts_at: startsAt, ends_at: endsAt, location: String(form.get("location")) }, { onSuccess: onClose, onError: (reason) => setError(message(reason, "Session could not be added. Please check the times and try again.")) });
  }
  return <div className="modal-backdrop"><section className="modal" role="dialog" aria-modal="true" aria-labelledby="session-modal-title"><header><div><span className="eyebrow">Workshop schedule</span><h2 id="session-modal-title">Add a session</h2></div><button type="button" className="icon-button" aria-label="Close" onClick={onClose}><X/></button></header><form onSubmit={submit}><label>Session title<input name="title" required maxLength={200} placeholder="e.g. Prompting foundations"/></label><div className="form-grid"><label>Date<input name="sessionDate" type="date" required/></label><label>Location<input name="location" placeholder="Room or online link"/></label><label>Starts at<input name="startsAt" type="time" required/></label><label>Ends at<input name="endsAt" type="time" required/></label></div>{error && <p className="form-error" role="alert">{error}</p>}<footer><button type="button" className="button secondary" onClick={onClose}>Cancel</button><button className="button primary" disabled={create.isPending}>{create.isPending ? "Adding..." : "Add session"}</button></footer></form></section></div>;
}
