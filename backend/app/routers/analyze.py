"""Analysis + pipeline endpoints (Instagram analysis, style profile, run)."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..models import PipelineJob, StyleProfile
from ..orchestrator import orchestrator
from ..store import store

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/projects/{project_id}/run")
def run_pipeline(project_id: str) -> PipelineJob:
    """Kick off the full analyze -> profile -> transcribe -> detect -> broll run."""
    if project_id not in store.projects:
        raise HTTPException(404, "Project not found")
    project = store.projects[project_id]
    job = orchestrator.create_job(project)
    orchestrator.run_async(job.id)
    return job


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> PipelineJob:
    if job_id not in store.pipeline_jobs:
        raise HTTPException(404, "Job not found")
    return store.pipeline_jobs[job_id]


@router.get("/projects/{project_id}/jobs")
def list_jobs(project_id: str) -> list[PipelineJob]:
    return [j for j in store.pipeline_jobs.values() if j.project_id == project_id]


# --------------------------- style profile --------------------------- #
@router.get("/style-profiles/{profile_id}")
def get_style_profile(profile_id: str) -> StyleProfile:
    if profile_id not in store.style_profiles:
        raise HTTPException(404, "Style profile not found")
    return store.style_profiles[profile_id]


@router.put("/style-profiles/{profile_id}")
def update_style_profile(profile_id: str, body: StyleProfile) -> StyleProfile:
    if profile_id not in store.style_profiles:
        raise HTTPException(404, "Style profile not found")
    body.id = profile_id
    body.updated_at = datetime.now(timezone.utc)
    store.style_profiles[profile_id] = body
    store.save()
    return body
