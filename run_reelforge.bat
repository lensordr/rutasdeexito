@echo off
REM ReelForge local launcher (Windows)
REM Starts the FastAPI backend and the Vite frontend in separate windows.

setlocal
set ROOT=%~dp0

echo ============================================
echo   ReelForge - starting backend + frontend
echo ============================================

REM --- Backend ---
if not exist "%ROOT%backend\.venv" (
  echo [backend] Creating virtual environment...
  python -m venv "%ROOT%backend\.venv"
  "%ROOT%backend\.venv\Scripts\python.exe" -m pip install --upgrade pip
  "%ROOT%backend\.venv\Scripts\python.exe" -m pip install -r "%ROOT%backend\requirements.txt"
)

start "ReelForge Backend" cmd /k "cd /d %ROOT%backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM --- Frontend ---
if not exist "%ROOT%frontend\node_modules" (
  echo [frontend] Installing npm packages...
  pushd "%ROOT%frontend"
  call npm install
  popd
)

start "ReelForge Frontend" cmd /k "cd /d %ROOT%frontend && npm run dev"

echo.
echo Backend : http://127.0.0.1:8000/api/health
echo Frontend: http://localhost:5173
echo.
echo Two terminal windows opened. Close them to stop the servers.
endlocal
