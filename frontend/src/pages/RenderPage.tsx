import { useCallback, useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api, type Clip, type RenderJob } from "../api";
import { Button, Card, PageHeader, StatusPill } from "../ui";

export default function RenderPage() {
  const { projectId } = useParams();
  const [clips, setClips] = useState<Clip[]>([]);
  const [jobs, setJobs] = useState<Record<string, RenderJob>>({});
  const pollRef = useRef<number | null>(null);

  const load = useCallback(async () => {
    if (!projectId) return;
    setClips(await api.listClips(projectId));
    const existing = await api.listRenderJobs(projectId);
    const map: Record<string, RenderJob> = {};
    for (const j of existing) map[j.clip_id] = j;
    setJobs(map);
  }, [projectId]);

  useEffect(() => {
    load();
  }, [load]);

  // Poll any running render jobs.
  useEffect(() => {
    const anyRunning = Object.values(jobs).some(
      (j) => j.status === "running" || j.status === "pending",
    );
    if (!anyRunning) {
      if (pollRef.current) window.clearInterval(pollRef.current);
      return;
    }
    pollRef.current = window.setInterval(async () => {
      const entries = await Promise.all(
        Object.values(jobs).map((j) => api.getRenderJob(j.id)),
      );
      setJobs((prev) => {
        const next = { ...prev };
        for (const j of entries) next[j.clip_id] = j;
        return next;
      });
    }, 600);
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current);
    };
  }, [jobs]);

  async function render(clip: Clip) {
    const job = await api.renderClip(clip.id);
    setJobs((prev) => ({ ...prev, [clip.id]: job }));
  }

  const selected = clips.filter((c) => c.selected);

  return (
    <div>
      <PageHeader
        title="Render"
        subtitle="Export selected clips as 9:16 reels. Engine: DaVinci Resolve (stubbed)."
      />

      {selected.length === 0 && (
        <div className="text-sm text-slate-400">
          No selected clips. Select clips on the Clips page first.
        </div>
      )}

      <div className="space-y-3">
        {selected.map((clip) => {
          const job = jobs[clip.id];
          const running =
            job && (job.status === "running" || job.status === "pending");
          return (
            <Card key={clip.id}>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="font-semibold text-white">
                    {clip.title.text}
                  </div>
                  {job && (
                    <div className="mt-1 flex items-center gap-3">
                      <StatusPill status={job.status} />
                      <span className="text-xs text-slate-500">
                        {job.message}
                      </span>
                    </div>
                  )}
                  {job && (
                    <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-ink-900 ring-1 ring-ink-600">
                      <div
                        className="h-full bg-brand-600 transition-all"
                        style={{ width: `${Math.round(job.progress * 100)}%` }}
                      />
                    </div>
                  )}
                  {job?.output_path && (
                    <div className="mt-2 truncate text-xs text-emerald-400">
                      → {job.output_path}
                    </div>
                  )}
                </div>
                <div className="ml-4">
                  <Button onClick={() => render(clip)} disabled={running}>
                    {running ? "Rendering…" : job ? "Re-render" : "Render"}
                  </Button>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
