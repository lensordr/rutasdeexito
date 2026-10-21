"""Render endpoints - trigger and track per-clip DaVinci Resolve renders."""
from __future__ import annotations

import threading
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..config import settings
from ..connectors.registry import registry
from ..models import JobStatus, RenderJob, StyleProfile
from ..store import store

router = APIRouter(prefix="/api", tags=["render"])


def _now():
    return datetime.now(timezone.utc)


def _render_worker(job_id: str):
    job = store.render_jobs[job_id]
    clip = store.clips[job.clip_id]
    project = store.projects[job.project_id]
    profile = (
        store.style_profiles.get(project.style_profile_id)
        if project.style_profile_id
        else None
    ) or StyleProfile()

    job.status = JobStatus.RUNNING
    store.save()

    def progress(frac: float, msg: str):
        job.progress = round(frac, 3)
        job.message = msg
        job.updated_at = _now()
        store.save()

    try:
        out = registry.render().render_clip(
            project, clip, profile, str(settings.output_dir), progress=progress
        )
        job.output_path = out
        job.status = JobStatus.COMPLETED
        job.progress = 1.0
        job.message = "Render complete"
        clip.render_job_id = job.id
        store.clips[clip.id] = clip
    except Exception as exc:  # noqa: BLE001
        job.status = JobStatus.FAILED
        job.message = str(exc)
    job.updated_at = _now()
    store.save()


@router.post("/clips/{clip_id}/render")
def render_clip(clip_id: str) -> RenderJob:
    if clip_id not in store.clips:
        raise HTTPException(404, "Clip not found")
    clip = store.clips[clip_id]
    job = RenderJob(project_id=clip.project_id, clip_id=clip_id)
    store.render_jobs[job.id] = job
    store.save()
    threading.Thread(target=_render_worker, args=(job.id,), daemon=True).start()
    return job


@router.get("/render-jobs/{job_id}")
def get_render_job(job_id: str) -> RenderJob:
    if job_id not in store.render_jobs:
        raise HTTPException(404, "Render job not found")
    return store.render_jobs[job_id]


@router.get("/projects/{project_id}/render-jobs")
def list_render_jobs(project_id: str) -> list[RenderJob]:
    return store.render_jobs_for_project(project_id)
