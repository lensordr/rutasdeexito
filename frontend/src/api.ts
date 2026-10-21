// Typed API client for the ReelForge backend.
// All requests go to /api and are proxied to the FastAPI server in dev.

export type JobStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "cancelled";

export interface Project {
  id: string;
  name: string;
  instagram_handle?: string | null;
  source_video_path?: string | null;
  source_duration_sec?: number | null;
  style_profile_id?: string | null;
  stage_status: Record<string, JobStatus>;
  created_at: string;
  updated_at: string;
}

export interface SubtitleStyle {
  font_family: string;
  font_size: number;
  font_color: string;
  highlight_color: string;
  stroke_color: string;
  stroke_width: number;
  position: string;
  uppercase: boolean;
  max_words_per_line: number;
}

export interface TitleStyle {
  font_family: string;
  font_size: number;
  font_color: string;
  background_color: string;
  background_opacity: number;
  position: string;
  padding: number;
}

export interface StyleProfile {
  id: string;
  name: string;
  source_handle?: string | null;
  target_duration_sec: number;
  min_duration_sec: number;
  max_duration_sec: number;
  hook_style: string;
  tone: string;
  aspect_ratio: string;
  subtitle: SubtitleStyle;
  title: TitleStyle;
  auto_zoom: boolean;
  zoom_intensity: number;
  use_broll: boolean;
  broll_density: number;
  notes: string;
  raw_analysis: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Subtitle {
  start_sec: number;
  end_sec: number;
  text: string;
}

export interface BrollInsertion {
  start_sec: number;
  end_sec: number;
  asset_id: string;
  source: string;
  url?: string | null;
  query?: string | null;
}

export interface Clip {
  id: string;
  project_id: string;
  source_start_sec: number;
  source_end_sec: number;
  score: number;
  reason: string;
  title: { text: string; editable: boolean };
  subtitles: Subtitle[];
  broll: BrollInsertion[];
  subtitle_style?: SubtitleStyle | null;
  title_style?: TitleStyle | null;
  selected: boolean;
  render_job_id?: string | null;
  created_at: string;
}

export interface StageResult {
  stage: string;
  status: JobStatus;
  message: string;
  started_at?: string | null;
  finished_at?: string | null;
  data: Record<string, unknown>;
}

export interface PipelineJob {
  id: string;
  project_id: string;
  status: JobStatus;
  stages: StageResult[];
  current_stage?: string | null;
  created_at: string;
  updated_at: string;
}

export interface RenderJob {
  id: string;
  project_id: string;
  clip_id: string;
  status: JobStatus;
  progress: number;
  message: string;
  output_path?: string | null;
  engine: string;
  created_at: string;
  updated_at: string;
}

export interface ConnectorStatus {
  key: string;
  label: string;
  connected: boolean;
  detail: string;
  is_stub: boolean;
  configured: boolean;
}

export interface ConnectorField {
  key: string;
  label: string;
  secret: boolean;
  required: boolean;
  placeholder: string;
  help: string;
}

export interface ConnectorSchema {
  key: string;
  label: string;
  description: string;
  fields: ConnectorField[];
}

export interface ConnectorValue {
  has_value: boolean;
  display: string;
}

export interface ConnectorDetail {
  schema: ConnectorSchema;
  values: Record<string, ConnectorValue>;
  status: Omit<ConnectorStatus, "key" | "label">;
}

export interface TestResult {
  ok: boolean;
  message: string;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => req<{ status: string }>("/api/health"),

  // Projects
  listProjects: () => req<Project[]>("/api/projects"),
  getProject: (id: string) => req<Project>(`/api/projects/${id}`),
  createProject: (body: {
    name: string;
    instagram_handle?: string;
    source_video_path?: string;
  }) =>
    req<Project>("/api/projects", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  updateProject: (id: string, body: Partial<Project>) =>
    req<Project>(`/api/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  deleteProject: (id: string) =>
    req<{ deleted: string }>(`/api/projects/${id}`, { method: "DELETE" }),

  // Pipeline
  runPipeline: (projectId: string) =>
    req<PipelineJob>(`/api/projects/${projectId}/run`, { method: "POST" }),
  getJob: (jobId: string) => req<PipelineJob>(`/api/jobs/${jobId}`),
  listJobs: (projectId: string) =>
    req<PipelineJob[]>(`/api/projects/${projectId}/jobs`),

  // Style profile
  getStyleProfile: (id: string) =>
    req<StyleProfile>(`/api/style-profiles/${id}`),
  updateStyleProfile: (id: string, body: StyleProfile) =>
    req<StyleProfile>(`/api/style-profiles/${id}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),

  // Clips
  listClips: (projectId: string) =>
    req<Clip[]>(`/api/projects/${projectId}/clips`),
  getClip: (id: string) => req<Clip>(`/api/clips/${id}`),
  updateClip: (
    id: string,
    body: {
      title_text?: string;
      selected?: boolean;
      subtitle_style?: SubtitleStyle;
      title_style?: TitleStyle;
    },
  ) =>
    req<Clip>(`/api/clips/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  suggestTitles: (id: string) =>
    req<{ suggestions: string[] }>(`/api/clips/${id}/suggest-titles`, {
      method: "POST",
    }),

  // Render
  renderClip: (clipId: string) =>
    req<RenderJob>(`/api/clips/${clipId}/render`, { method: "POST" }),
  getRenderJob: (id: string) => req<RenderJob>(`/api/render-jobs/${id}`),
  listRenderJobs: (projectId: string) =>
    req<RenderJob[]>(`/api/projects/${projectId}/render-jobs`),

  // Connectors
  listConnectors: () => req<ConnectorStatus[]>("/api/connectors"),
  getConnector: (key: string) =>
    req<ConnectorDetail>(`/api/connectors/${key}`),
  saveConnector: (key: string, values: Record<string, string>) =>
    req<{ saved: boolean; values: Record<string, ConnectorValue>; status: ConnectorDetail["status"] }>(
      `/api/connectors/${key}`,
      { method: "PUT", body: JSON.stringify({ values }) },
    ),
  testConnector: (key: string) =>
    req<TestResult>(`/api/connectors/${key}/test`, { method: "POST" }),
};
