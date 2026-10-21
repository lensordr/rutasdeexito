"""Clip listing, editing, and AI title suggestions."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..connectors.registry import registry
from ..models import Clip, ClipTitle, SubtitleStyle, TitleStyle
from ..store import store

router = APIRouter(prefix="/api", tags=["clips"])


class ClipUpdate(BaseModel):
    title_text: Optional[str] = None
    selected: Optional[bool] = None
    subtitle_style: Optional[SubtitleStyle] = None
    title_style: Optional[TitleStyle] = None


@router.get("/projects/{project_id}/clips")
def list_clips(project_id: str) -> list[Clip]:
    return store.clips_for_project(project_id)


@router.get("/clips/{clip_id}")
def get_clip(clip_id: str) -> Clip:
    if clip_id not in store.clips:
        raise HTTPException(404, "Clip not found")
    return store.clips[clip_id]


@router.patch("/clips/{clip_id}")
def update_clip(clip_id: str, body: ClipUpdate) -> Clip:
    if clip_id not in store.clips:
        raise HTTPException(404, "Clip not found")
    clip = store.clips[clip_id]
    if body.title_text is not None:
        clip.title = ClipTitle(text=body.title_text)
    if body.selected is not None:
        clip.selected = body.selected
    if body.subtitle_style is not None:
        clip.subtitle_style = body.subtitle_style
    if body.title_style is not None:
        clip.title_style = body.title_style
    store.clips[clip_id] = clip
    store.save()
    return clip


@router.post("/clips/{clip_id}/suggest-titles")
def suggest_titles(clip_id: str) -> dict:
    if clip_id not in store.clips:
        raise HTTPException(404, "Clip not found")
    clip = store.clips[clip_id]
    project = store.projects.get(clip.project_id)
    profile = None
    if project and project.style_profile_id:
        profile = store.style_profiles.get(project.style_profile_id)
    if profile is None:
        from ..models import StyleProfile

        profile = StyleProfile()
    titles = registry.claude_code().suggest_titles(clip, profile)
    return {"suggestions": titles}
