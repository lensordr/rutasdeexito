import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, type PipelineJob, type Project } from "../api";
import { Button, Card, ErrorBox, PageHeader, StatusPill, cardHover } from "../ui";

const STAGE_LABELS: Record<string, string> = {
  analyze_instagram: "Analyze Instagram",
  build_style_profile: "Build Style Profile",
  transcribe: "Transcribe Podcast",
  detect_clips: "Detect Clips",
  fetch_broll: "Fetch B-roll",
  render: "Render (per-clip)",
};

export default function ProjectDetailPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [job, setJob] = useState<PipelineJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<number | null>(null);

  const loadProject = useCallback(async () => {
    if (!projectId) return;
    try {
      setProject(await api.getProject(projectId));
      const jobs = await api.listJobs(projectId);
      if (jobs.length) setJob(jobs[jobs.length - 1]);
    } catch (e) {
      setError(String(e));
    }
  }, [projectId]);

  useEffect(() => {
    loadProject();
  }, [loadProject]);

  // Poll the active job while it is running.
  useEffect(() => {
    if (!job || (job.status !== "running" && job.status !== "pending")) {
      if (pollRef.current) window.clearInterval(pollRef.current);
      return;
    }
    pollRef.current = window.setInterval(async () => {
      try {
        const fresh = await api.getJob(job.id);
        setJob(fresh);
        if (fresh.status === "completed" || fresh.status === "failed") {
          if (pollRef.current) window.clearInterval(pollRef.current);
          loadProject();
        }
      } catch {
        /* ignore transient polling errors */
      }
    }, 800);
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, [job, loadProject]);

  async function runPipeline() {
    if (!projectId) return;
    try {
      const j = await api.runPipeline(projectId);
      setJob(j);
    } catch (e) {
      setError(String(e));
    }
  }

  if (!project) {
    return <div className="text-sm text-slate-400">Loading…</div>;
  }

  const running = job?.status === "running" || job?.status === "pending";

  return (
    <div>
      <PageHeader
        title={project.name}
        subtitle={project.instagram_handle || "no handle"}
        actions={
          <Button onClick={runPipeline} disabled={running}>
            {running ? "Running…" : "Run pipeline"}
          </Button>
        }
      />

      {error && <ErrorBox message={error} />}

      <Card className="mb-6">
        <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Pipeline stages
        </div>
        {!job && (
          <div className="text-sm text-slate-500">
            No run yet. Click “Run pipeline” to analyze, profile, transcribe and
            detect clips (all stubbed for now).
          </div>
        )}
        {job && (
          <ol className="space-y-2">
            {job.stages.map((s) => (
              <li
                key={s.stage}
                className="flex items-center justify-between rounded-lg border border-ink-600 bg-ink-900 px-4 py-2.5"
              >
                <div>
                  <div className="text-sm font-medium text-slate-100">
                    {STAGE_LABELS[s.stage] ?? s.stage}
                  </div>
                  {s.message && (
                    <div className="text-xs text-slate-500">{s.message}</div>
                  )}
                </div>
                <StatusPill status={s.status} />
              </li>
            ))}
          </ol>
        )}
      </Card>

      <div className="grid grid-cols-3 gap-4">
        <Card className={cardHover}>
          <div onClick={() => navigate(`/projects/${project.id}/style`)}>
            <div className="font-semibold text-white">Style Profile</div>
            <div className="text-sm text-slate-500">
              Customize the reel creation guide.
            </div>
          </div>
        </Card>
        <Card className={cardHover}>
          <div onClick={() => navigate(`/projects/${project.id}/clips`)}>
            <div className="font-semibold text-white">Clips</div>
            <div className="text-sm text-slate-500">
              Review and edit detected clips.
            </div>
          </div>
        </Card>
        <Card className={cardHover}>
          <div onClick={() => navigate(`/projects/${project.id}/render`)}>
            <div className="font-semibold text-white">Render</div>
            <div className="text-sm text-slate-500">
              Export 9:16 reels via DaVinci.
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
