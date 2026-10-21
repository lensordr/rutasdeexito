# Setup Guide — Rutas de Éxito (Windows)

How to clone, install, and run the app on a fresh Windows machine. After this,
you re-enter your API keys in the app's **Connectors & Settings** page (they
are never stored in the repo).

---

## Prerequisites

Install these first:

1. **Git** — https://git-scm.com/download/win
2. **Python 3.11+** — https://www.python.org/downloads/
   - During install, check **"Add python.exe to PATH"**.
3. **Node.js 18+ (LTS)** — https://nodejs.org/
4. *(Later, for real rendering)* **DaVinci Resolve Studio** — already licensed.

Verify in a new terminal:
```bat
git --version
python --version
node --version
npm --version
```

---

## 1. Clone the repo

```bat
cd %USERPROFILE%\Desktop
git clone https://github.com/lensordr/rutasdeexito.git
cd rutasdeexito
```

---

## 2. One-click run (recommended)

From the project root:
```bat
run_reelforge.bat
```

On first run this will:
- create the Python virtual environment in `backend\.venv`
- install backend dependencies (`backend\requirements.txt`)
- install frontend dependencies (`npm install`)
- open two terminal windows (backend + frontend)

Then open:
- **App (UI)**: http://localhost:5173
- **API health**: http://127.0.0.1:8000/api/health

To stop: close the two opened terminal windows.

---

## 3. Manual run (if you prefer, or for debugging)

### Backend
```bat
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend (second terminal)
```bat
cd frontend
npm install
npm run dev
```

---

## 4. Re-enter your API keys (per machine)

Secrets are **not** in the repo (by design). On each machine:

1. Open the app → **Connectors & Settings**.
2. Expand a connector, fill its fields, click **Save**.
3. Click **Test connection** to confirm it's configured.

Keys you may add (all optional until that integration is wired):

| Connector | Fields |
|-----------|--------|
| Instagram | Business Account ID, Access Token |
| Transcription | Provider, OpenAI API Key (if using OpenAI) |
| Clip Detector | Anthropic API Key (optional) |
| B-roll | Pexels API Key, Storyblocks Key + Secret |
| DaVinci Resolve | Scripting API path, fusionscript.dll path |
| Claude Code | Anthropic API Key |

Values are saved locally to `backend\data\connector_config.json` (gitignored).

---

## 5. Using the app

1. **Projects** → create a project (name, Instagram handle, path to your 16:9
   podcast file).
2. Open the project → **Run pipeline** (currently uses stub data).
3. **Style Profile** → tweak the reel creation guide.
4. **Clips** → review detected clips, edit titles, toggle selection.
5. **Render** → export selected clips (stubbed output path for now).

---

## 6. Troubleshooting

- **`python` not found** → reinstall Python with "Add to PATH" checked, open a
  new terminal.
- **`npm` not found** → reinstall Node.js LTS, open a new terminal.
- **Port already in use** → close old server windows, or change the port
  (backend: `--port`, frontend: `vite.config.ts` → `server.port`).
- **Frontend can't reach backend** → ensure the backend is running on
  `127.0.0.1:8000`; the frontend proxies `/api` to it (see `vite.config.ts`).
- **PowerShell `&&` error** → use `;` between commands, or run them separately.

---

## 7. What's real vs stubbed

Everything runs today on **stub data**. See **DOCUMENTATION.md** section 5 for
the roadmap of which integrations become real and in what order
(recommended first: local Whisper transcription).
