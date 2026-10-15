import { GraduationCap, LogOut } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router";
import { useLogout, useMe } from "@/features/auth/queries";
import { Toaster } from "./toaster";

const navItems = [
  { to: "/", label: "Workshops", icon: GraduationCap },
];

export function Layout() {
  const me = useMe();
  const logout = useLogout();
  const navigate = useNavigate();
  const initials = (me.data?.email ?? "SN").slice(0, 2).toUpperCase();
  return <div className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark">S</span><div><strong>SCHOOLNET</strong><small>Learning for life</small></div></div><div className="topbar-path"><span>Workspace</span><b>/</b><strong>Workshop Hub</strong></div><div className="profile"><span>{me.data?.email}</span><button aria-label="Open profile">{initials}</button></div></header>
    <aside className="sidebar"><div className="workspace-title"><span>W</span><div><strong>Workshop Hub</strong><small>Attendance Management</small></div></div><p className="nav-label">Workspace</p><nav aria-label="Workspace navigation">{navItems.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} end={to === "/"}><Icon size={19}/><span>{label}</span></NavLink>)}</nav><div className="sidebar-footer"><div><i/> Secure workspace</div><small>Schoolnet India Limited</small><button onClick={() => logout.mutate(undefined, { onSuccess: () => navigate("/login", { replace: true }) })}><LogOut size={16}/> Sign out</button></div></aside>
    <main className="main-content"><Outlet/></main><Toaster/>
  </div>;
}
