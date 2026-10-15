import { Plus, Search } from "lucide-react";
import { useEffect } from "react";
import { useWorkshopUiStore } from "@/stores/workshop-ui-store";
import { useWorkshops } from "./hooks";
import { StudentModal } from "./student-modal";
import { WorkshopDetail } from "./workshop-detail";
import { WorkshopModal } from "./workshop-modals";

export function WorkshopsPage() {
  const query = useWorkshops();
  const selectedId = useWorkshopUiStore((state) => state.selectedId);
  const select = useWorkshopUiStore((state) => state.select);
  const search = useWorkshopUiStore((state) => state.search);
  const setSearch = useWorkshopUiStore((state) => state.setSearch);
  const modalOpen = useWorkshopUiStore((state) => state.studentModalOpen);
  const setModal = useWorkshopUiStore((state) => state.setStudentModal);
  const workshopModalOpen = useWorkshopUiStore((state) => state.workshopModalOpen);
  const setWorkshopModal = useWorkshopUiStore((state) => state.setWorkshopModal);
  const workshops = query.data ?? [];
  useEffect(() => { if (!selectedId && workshops[0]) select(workshops[0].id); }, [selectedId, select, workshops]);
  const visible = workshops.filter((workshop) => workshop.title.toLowerCase().includes(search.toLowerCase()));
  const active = workshops.filter((workshop) => workshop.status === "active");
  return <><section className="page-heading"><div><span className="eyebrow">Learning together</span><h1>Workshops</h1><p>Manage workshops, people, sessions, and participation.</p></div><div className="heading-actions"><button className="button secondary" onClick={() => setWorkshopModal(true)}><Plus/> New workshop</button><button className="button primary" onClick={() => setModal(true)} disabled={!selectedId}><Plus/> Add student</button></div></section><section className="stat-grid" aria-label="Workspace statistics"><article><span>Active workshops</span><strong>{active.length}</strong><small>Across your workspace</small></article><article><span>Active students</span><strong>{workshops.reduce((sum, item) => sum + item.student_count, 0)}</strong><small>Current enrolments</small></article><article><span>Scheduled sessions</span><strong>{workshops.reduce((sum, item) => sum + item.session_count, 0)}</strong><small>Learning events</small></article><article><span>Total workshops</span><strong>{workshops.length}</strong><small>All statuses</small></article></section>
  <section className="workspace-grid"><aside className="workshop-list"><div className="panel-heading"><h2>All workshops</h2><span>{workshops.length}</span></div><label className="search"><Search/><input type="search" aria-label="Find a workshop" placeholder="Find a workshop" value={search} onChange={(event) => setSearch(event.target.value)}/></label>{query.isPending && <p>Loading workshops...</p>}{query.isError && <div className="inline-error">Could not load workshops.<button onClick={() => void query.refetch()}>Retry</button></div>}<div className="list-label">Workshops</div>{visible.map((workshop) => <button key={workshop.id} className={`workshop-item ${selectedId === workshop.id ? "active" : ""}`} onClick={() => select(workshop.id)}><strong>{workshop.title}</strong><span>{workshop.facilitator_name || workshop.status}</span><small>{workshop.student_count} students · {workshop.session_count} sessions</small></button>)}{!query.isPending && visible.length === 0 && <p>No workshops found.</p>}</aside>{selectedId ? <WorkshopDetail id={selectedId}/> : <section className="state-card"><h2>{workshops.length === 0 ? "Create your first workshop" : "Select a workshop"}</h2><p>{workshops.length === 0 ? "Set up a workshop, add sessions and enrol students to begin." : "Choose a workshop to see its details."}</p>{workshops.length === 0 && <button className="button primary" onClick={() => setWorkshopModal(true)}>Create workshop</button>}</section>}</section>{modalOpen && selectedId && <StudentModal workshopId={selectedId} onClose={() => setModal(false)}/>} {workshopModalOpen && <WorkshopModal onClose={() => setWorkshopModal(false)}/>}</>;
}
