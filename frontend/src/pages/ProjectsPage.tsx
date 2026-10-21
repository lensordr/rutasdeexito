import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, type Project } from "../api";
import { Button, Card, ErrorBox, Field, PageHeader, cardHover, inputClass } from "../ui";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [handle, setHandle] = useState("");
  const [videoPath, setVideoPath] = useState("");
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function load() {
    try {
      setProjects(await api.listProjects());
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function createProject(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      const p = await api.createProject({
        name,
        instagram_handle: handle || undefined,
        source_video_path: videoPath || undefined,
      });
      setName("");
      setHandle("");
      setVideoPath("");
      navigate(`/projects/${p.id}`);
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div>
      <PageHeader
        title="Projects"
        subtitle="Each project turns one raw podcast into a batch of reels."
      />

      {error && <ErrorBox message={error} />}

      <Card className="mb-6">
        <form onSubmit={createProject} className="grid grid-cols-3 gap-4">
          <Field label="Project name">
            <input
              className={inputClass}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Episode 42"
            />
          </Field>
          <Field label="Instagram handle">
            <input
              className={inputClass}
              value={handle}
              onChange={(e) => setHandle(e.target.value)}
              placeholder="@yourpage"
            />
          </Field>
          <Field label="Source video path (16:9)">
            <input
              className={inputClass}
              value={videoPath}
              onChange={(e) => setVideoPath(e.target.value)}
              placeholder="C:\\podcasts\\ep42.mp4"
            />
          </Field>
          <div className="col-span-3">
            <Button type="submit">Create project</Button>
          </div>
        </form>
      </Card>

      <div className="grid grid-cols-2 gap-4">
        {projects.map((p) => (
          <Card
            key={p.id}
            className={cardHover}
          >
            <div
              onClick={() => navigate(`/projects/${p.id}`)}
              className="flex items-start justify-between"
            >
              <div>
                <div className="font-semibold text-white">{p.name}</div>
                <div className="text-sm text-brand-400">
                  {p.instagram_handle || "no handle"}
                </div>
                <div className="mt-2 truncate text-xs text-slate-500">
                  {p.source_video_path || "no source video"}
                </div>
              </div>
            </div>
          </Card>
        ))}
        {projects.length === 0 && (
          <div className="col-span-2 py-8 text-center text-sm text-slate-400">
            No projects yet. Create one above.
          </div>
        )}
      </div>
    </div>
  );
}
