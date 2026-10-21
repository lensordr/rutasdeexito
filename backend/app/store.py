"""
Tiny JSON-backed store.

Keeps all entities in memory and persists them to a single JSON file on
every write. Good enough for a local single-user skeleton; swap for a real
DB later behind the same method surface.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Optional

from .config import settings
from .models import (
    Clip,
    PipelineJob,
    Project,
    RenderJob,
    StyleProfile,
)


class Store:
    def __init__(self, path: Optional[Path] = None):
        self._path = path or (settings.data_dir / "store.json")
        self._lock = threading.RLock()
        self.projects: dict[str, Project] = {}
        self.style_profiles: dict[str, StyleProfile] = {}
        self.clips: dict[str, Clip] = {}
        self.render_jobs: dict[str, RenderJob] = {}
        self.pipeline_jobs: dict[str, PipelineJob] = {}
        self._load()

    # ----------------------------- persistence ---------------------------- #
    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return
        self.projects = {k: Project(**v) for k, v in raw.get("projects", {}).items()}
        self.style_profiles = {
            k: StyleProfile(**v) for k, v in raw.get("style_profiles", {}).items()
        }
        self.clips = {k: Clip(**v) for k, v in raw.get("clips", {}).items()}
        self.render_jobs = {
            k: RenderJob(**v) for k, v in raw.get("render_jobs", {}).items()
        }
        self.pipeline_jobs = {
            k: PipelineJob(**v) for k, v in raw.get("pipeline_jobs", {}).items()
        }

    def _dump(self) -> None:
        def ser(d):
            return {k: v.model_dump(mode="json") for k, v in d.items()}

        payload = {
            "projects": ser(self.projects),
            "style_profiles": ser(self.style_profiles),
            "clips": ser(self.clips),
            "render_jobs": ser(self.render_jobs),
            "pipeline_jobs": ser(self.pipeline_jobs),
        }
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        tmp.replace(self._path)

    def save(self) -> None:
        with self._lock:
            self._dump()

    # ------------------------------- helpers ------------------------------ #
    def clips_for_project(self, project_id: str) -> list[Clip]:
        return [c for c in self.clips.values() if c.project_id == project_id]

    def render_jobs_for_project(self, project_id: str) -> list[RenderJob]:
        return [r for r in self.render_jobs.values() if r.project_id == project_id]


store = Store()
