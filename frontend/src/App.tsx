import { NavLink, Outlet, useParams } from "react-router-dom";

function SideLink({ to, label, end }: { to: string; label: string; end?: boolean }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `group relative block rounded-lg px-3 py-2 text-sm font-medium transition ${
          isActive
            ? "bg-brand-600 text-white shadow-glow"
            : "text-slate-400 hover:bg-ink-700 hover:text-white"
        }`
      }
    >
      {({ isActive }) => (
        <span className="flex items-center gap-2">
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              isActive ? "bg-white" : "bg-brand-600/0 group-hover:bg-brand-600"
            }`}
          />
          {label}
        </span>
      )}
    </NavLink>
  );
}

export default function App() {
  const { projectId } = useParams();

  return (
    <div className="flex h-full">
      <aside className="relative z-10 flex w-64 flex-col border-r border-ink-600 bg-ink-800/95 p-4 backdrop-blur">
        <div className="mb-8 px-1">
          <img
            src="/logo.png"
            alt="Rutas de Éxito"
            className="w-full rounded-lg"
          />
        </div>

        <nav className="space-y-1">
          <SideLink to="/" label="Projects" end />
          <SideLink to="/connectors" label="Connectors & Settings" />
        </nav>

        {projectId && (
          <>
            <div className="mt-7 mb-2 px-3 text-[11px] font-semibold uppercase tracking-widest text-slate-600">
              Current project
            </div>
            <nav className="space-y-1">
              <SideLink to={`/projects/${projectId}`} label="Overview" end />
              <SideLink to={`/projects/${projectId}/style`} label="Style Profile" />
              <SideLink to={`/projects/${projectId}/clips`} label="Clips" />
              <SideLink to={`/projects/${projectId}/render`} label="Render" />
            </nav>
          </>
        )}

        <div className="mt-auto flex items-center gap-2 px-3 pt-6 text-[11px] text-slate-600">
          <span className="h-1.5 w-1.5 rounded-full bg-brand-600" />
          Skeleton build · integrations stubbed
        </div>
      </aside>

      <main className="relative flex-1 overflow-y-auto">
        {/* Faded logo watermark behind all content */}
        <div
          aria-hidden
          className="pointer-events-none fixed inset-y-0 right-0 left-64 z-0 flex items-center justify-center"
        >
          <img
            src="/logo.png"
            alt=""
            className="w-[70%] max-w-3xl select-none opacity-[0.05] blur-[1px]"
          />
        </div>

        <div className="relative z-10 mx-auto max-w-5xl px-8 py-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
