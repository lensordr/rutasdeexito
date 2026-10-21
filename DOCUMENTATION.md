# Rutas de Éxito — Project Documentation

> Internal "OpusClip-style" tool: turn one long 16:9 podcast into multiple
> personalized 9:16 Instagram reels, styled to the **Rutas de Éxito** page,
> rendered with DaVinci Resolve.

This document is the single source of truth for **what is built**, **what is
stubbed**, and **what remains to do**. Read this first after cloning.

---

## 1. Current status (snapshot)

**Stage: working skeleton.** The full pipeline runs end to end through the UI,
but every external integration is a **stub** returning sample data. You can
click through the entire workflow today; it just isn't calling real services
yet.

| Area | Status |
|------|--------|
| Local web app (backend + frontend) | ✅ Working |
| Black / red / white themed UI + logo watermark | ✅ Working |
| Project creation + pipeline run | ✅ Working (stubbed data) |
| Style Profile editor | ✅ Working (editable, persisted) |
| Clip review (titles, selection, AI suggestions) | ✅ Working (stubbed) |
| Render page (progress tracking) | ✅ Working (stubbed output) |
| Connectors & Settings (add API keys in UI) | ✅ Working (saves + tests, GitHub-safe) |
| Real Instagram / Whisper / DaVinci / Pexels / Claude | ❌ Not yet (stubs) |

---

## 2. Architecture

A **local web app**:

- **Backend**: Python + FastAPI (`backend/app`)
- **Frontend**: React + Vite + TypeScript + Tailwind (`frontend`)
- **Storage**: JSON files under `backend/data/` (gitignored)
- **OS target**: Windows-first

```
┌─────────────────────────────────────────────┐
│                  Interface (UI)               │
│  Projects · Style · Clips · Render · Settings │
└───────────────────┬───────────────────────────┘
                    │  REST (/api/*)
┌───────────────────▼───────────────────────────┐
│                 Orchestrator                    │
│      (pipeline runner + job state + config)     │
└───┬────────┬────────┬────────┬────────┬─────────┘
    │        │        │        │        │
 Instagram  Style   Transcribe  Clip    Render
 Analyzer  Profiler  Connector Detector Connector
    │                                     │
 B-roll Connector ── Claude Connector ────┘
         (all are swappable stubs today)
```

### The connector pattern (most important concept)

Every external integration is an **abstract interface** in
`backend/app/connectors/base.py`. The app depends only on the interface, never
on a concrete implementation. Stubs live in `connectors/stubs.py`; the
`registry.py` maps each key to an implementation and injects saved config.

To make an integration real: implement its base class, swap the entry in the
registry, done. Nothing else in the app changes.

| Connector | Interface | Current impl |
|-----------|-----------|--------------|
| Instagram | `InstagramConnector` | `StubInstagram` |
| Style Profiler | `StyleProfilerConnector` | `StubStyleProfiler` |
| Transcription | `TranscriptionConnector` | `StubTranscription` |
| Clip Detector | `ClipDetectorConnector` | `StubClipDetector` |
| B-roll | `BrollConnector` | `StubBroll` |
| DaVinci Resolve render | `RenderConnector` | `StubRender` |
| Claude Code | `ClaudeCodeConnector` | `StubClaudeCode` |

---

## 3. What exists now (detailed)

### Backend (`backend/app`)
- `main.py` — FastAPI app, CORS, routers, `/api/health`.
- `config.py` — settings, data/output dirs, CORS origins, host/port.
- `models.py` — Pydantic models: `Project`, `StyleProfile`, `Clip`,
  `RenderJob`, `PipelineJob`, plus `Subtitle`, `BrollInsertion`, styles.
- `store.py` — JSON-backed store (`backend/data/store.json`).
- `orchestrator.py` — runs the 6 pipeline stages on a background thread and
  tracks per-stage status.
- `connector_config.py` — field definitions per connector, secret masking,
  and persistence to `backend/data/connector_config.json` (gitignored).
- `connectors/` — `base.py` (interfaces), `stubs.py`, `registry.py`.
- `routers/` — `projects.py`, `analyze.py`, `clips.py`, `render.py`,
  `connectors.py`.

### Frontend (`frontend/src`)
- `api.ts` — typed API client mirroring backend models.
- `App.tsx` — shell, sidebar nav, logo watermark.
- `ui.tsx` — shared components (Card, Button, StatusPill, Field, ErrorBox).
- `pages/` — `ProjectsPage`, `ProjectDetailPage`, `StyleProfilePage`,
  `ClipsPage`, `RenderPage`, `ConnectorsPage`.

### Pipeline stages (what "Run pipeline" does)
1. **Analyze Instagram** — fetch recent reels (stub: sample metadata).
2. **Build Style Profile** — synthesize the reel guide (stub: from averages).
3. **Transcribe** — produce timed subtitles (stub: fake transcript).
4. **Detect Clips** — score + extract candidate clips (stub: heuristic).
5. **Fetch B-roll** — suggest stock insertions (stub: placeholder URLs).
6. **Render** — triggered per-clip from the Render page (stub: fake path).

### Connectors & Settings (usable today)
- Expandable card per connector with its fields.
- Secret fields are password-masked; saved secrets return as `••••••`.
- **Save** persists to `backend/data/connector_config.json` (gitignored).
- **Test connection** runs the connector's health check.
- Status badge: `not set` → `configured` → (later) `connected`.

---

## 4. What has been verified

- Backend imports cleanly; all routes and 7 connectors resolve.
- Full stubbed pipeline run completes and produces clips + a style profile.
- Live HTTP tests: create project, run pipeline, list clips, save a connector
  key (returned masked), test connection, state persists.
- Frontend builds cleanly under strict TypeScript (Vite production build).
- GitHub-safety: `git check-ignore` confirms `connector_config.json` and
  `.env` are excluded; a dry-run `git add` does not stage secret files.

---

## 5. Roadmap — what remains to do

Ordered by recommended priority. Each item names the file(s) to touch.

### Phase 1 — Make the content real (highest value)
1. **Transcription (local Whisper)** — *recommended first.*
   - Implement `WhisperTranscription(TranscriptionConnector)` in a new
     `connectors/real/transcription_whisper.py`.
   - Use `faster-whisper` or `openai-whisper`; return real `Subtitle` list.
   - Register in `registry.py`. Add `ffmpeg` dependency note.
   - Unlocks genuine clip detection.
2. **Clip Detector (real)** — score transcript windows by hook strength,
   retention cues, sentence boundaries; optionally call Claude for ranking.
   - Implement `RealClipDetector(ClipDetectorConnector)`.

### Phase 2 — Make the render real
3. **DaVinci Resolve render connector** — the biggest piece.
   - Implement `ResolveRender(RenderConnector)` using Resolve's Python
     scripting API (`DaVinciResolveScript`).
   - Steps: import source, create 9:16 timeline, set in/out per clip,
     add subtitle track (burned-in via Text+ or Fusion), apply auto-zoom
     (keyframed transform), insert b-roll on an upper track, add a title
     card with background, then render/export the clip.
   - Read paths from the Resolve connector config (already in the UI).
   - This requires Resolve Studio running locally.

### Phase 3 — External data sources
4. **Instagram Graph API** — real `fetch_recent_reels` using Business account
   + long-lived token (both already captured in the UI).
5. **Style Profiler (real)** — derive durations, hook patterns, caption style,
   colors/fonts from the fetched reels (optionally LLM-assisted).
6. **B-roll (Pexels / Storyblocks)** — real search + download using saved keys;
   map clip keywords to stock queries.
7. **Claude Code connector** — real title/hook generation and edit suggestions
   using the Anthropic API key.

### Phase 4 — Polish & productization
8. **Connection tests** — make "Test connection" perform a real lightweight
   API ping per connector (currently reports "configured", not "reachable").
9. **Media upload** — let the user pick/drag the source video in the UI
   instead of typing a path.
10. **Preview** — show a 9:16 preview of a clip (subtitles/title overlay)
    before rendering.
11. **Batch render + queue** — render all selected clips with a job queue.
12. **Auth / multi-user** (only if ever hosted beyond local).
13. **Database** — swap the JSON store for SQLite/Postgres if data grows.
14. **Packaging** — one-click installer or bundled launcher.
15. **Tests** — add pytest (backend) + component tests (frontend).

---

## 6. Known limitations (today)

- All integrations are stubs — no real Instagram, transcription, render, etc.
- "Test connection" only confirms config is saved, not that credentials work.
- Source video is a typed path, not an upload.
- Single-user, local only. JSON store (not a database).
- No automated test suite yet.

---

## 7. Where things are stored

| Data | Location | Committed? |
|------|----------|-----------|
| App data (projects, clips, jobs) | `backend/data/store.json` | ❌ gitignored |
| Connector keys/paths | `backend/data/connector_config.json` | ❌ gitignored |
| Rendered outputs | `backend/output/` | ❌ gitignored |
| Env overrides | `backend/.env` | ❌ gitignored |
| Env template | `.env.example` | ✅ committed |

See **SETUP.md** for how to install and run after cloning.
