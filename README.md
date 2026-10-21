# Rutas de Éxito

A local web app that turns one long 16:9 podcast into multiple personalized
**9:16 Instagram reels** — an OpusClip-style workflow tailored to the
**Rutas de Éxito** page, with **DaVinci Resolve** as the render engine.

> **Status: working skeleton.** The full pipeline runs end to end through the
> UI, but every external integration is currently a **stub** returning sample
> data. You connect the real services (Instagram, transcription, DaVinci,
> Pexels, Claude) later from the **Connectors & Settings** page — no code
> edits, and no secrets ever committed to GitHub.

## Documentation

- **[SETUP.md](SETUP.md)** — install and run on a fresh Windows machine.
- **[DOCUMENTATION.md](DOCUMENTATION.md)** — full architecture, current state,
  and the roadmap of what's left to build.

## Quick start (Windows)

```bat
git clone https://github.com/lensordr/rutasdeexito.git
cd rutasdeexito
run_reelforge.bat
```

Then open **http://localhost:5173**.

See [SETUP.md](SETUP.md) for prerequisites (Git, Python 3.11+, Node 18+) and
manual steps.

## What it does

1. **Analyze Instagram** — pull your recent reels.
2. **Build a Style Profile** — the editable "reel creation guide".
3. **Transcribe** the podcast into timed subtitles.
4. **Detect clips** — score and extract the best moments.
5. **Fetch b-roll** — suggest stock footage per clip.
6. **Render** — export each clip as a 9:16 reel with subtitles, zooms, b-roll
   and a title card, via DaVinci Resolve.

## Stack

- **Backend**: Python + FastAPI (`backend/`)
- **Frontend**: React + Vite + TypeScript + Tailwind (`frontend/`)
- **Storage**: JSON files under `backend/data/` (gitignored)
- **OS**: Windows-first

## Security / GitHub safety

API keys and paths entered in the app are stored **only on your machine** in
`backend/data/connector_config.json`, which is gitignored. Clone on any
machine and re-enter keys in the UI. Nothing secret is committed.
