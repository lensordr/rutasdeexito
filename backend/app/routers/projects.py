"""Project CRUD endpoints."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models import Project
from ..store import store

router = APIRouter(prefix="/api/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str
    instagram_handle: Optional[str] = None
    source_video_path: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    instagram_handle: Optional[str] = None
    source_video_path: Optional[str] = None
    style_profile_id: Optional[str] = None


@router.get("")
def list_projects() -> list[Project]:
    return list(store.projects.values())


@router.post("")
def create_project(body: ProjectCreate) -> Project:
    project = Project(**body.dict())
    store.projects[project.id] = project
    store.save()
    return project


@router.get("/{project_id}")
def get_project(project_id: str) -> Project:
    if project_id not in store.projects:
        raise HTTPException(404, "Project not found")
    return store.projects[project_id]


@router.patch("/{project_id}")
def update_project(project_id: str, body: ProjectUpdate) -> Project:
    if project_id not in store.projects:
        raise HTTPException(404, "Project not found")
    project = store.projects[project_id]
    for k, v in body.dict(exclude_unset=True).items():
        setattr(project, k, v)
    project.updated_at = datetime.now(timezone.utc)
    store.save()
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str) -> dict:
    if project_id not in store.projects:
        raise HTTPException(404, "Project not found")
    del store.projects[project_id]
    for c in store.clips_for_project(project_id):
        store.clips.pop(c.id, None)
    store.save()
    return {"deleted": project_id}
