"""
Core data models for ReelForge.

These Pydantic models are the shared contracts between the API layer,
the pipeline orchestrator, and the connectors. They are intentionally
storage-agnostic: the current store serializes them to JSON on disk,
but they could later back onto a database without changing the API.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


def _uid() -> str:
    return uuid.uuid4().hex[:12]


def _now() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #
class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStage(str, Enum):
    ANALYZE_INSTAGRAM = "analyze_instagram"
    BUILD_STYLE_PROFILE = "build_style_profile"
    TRANSCRIBE = "transcribe"
    DETECT_CLIPS = "detect_clips"
    FETCH_BROLL = "fetch_broll"
    RENDER = "render"


class AspectRatio(str, Enum):
    VERTICAL_9_16 = "9:16"
    SQUARE_1_1 = "1:1"
    HORIZONTAL_16_9 = "16:9"


# --------------------------------------------------------------------------- #
# Style profile (the "reel creation guide")
# --------------------------------------------------------------------------- #
class SubtitleStyle(BaseModel):
    font_family: str = "Montserrat"
    font_size: int = 72
    font_color: str = "#FFFFFF"
    highlight_color: str = "#FFE000"
    stroke_color: str = "#000000"
    stroke_width: int = 6
    position: str = "center"  # top | center | bottom
    uppercase: bool = True
    max_words_per_line: int = 4


class TitleStyle(BaseModel):
    font_family: str = "Montserrat"
    font_size: int = 90
    font_color: str = "#FFFFFF"
    background_color: str = "#111111"
    background_opacity: float = 0.85
    position: str = "top"  # top | center
    padding: int = 40


class StyleProfile(BaseModel):
    """The personalized ruleset derived from the user's Instagram page.

    Produced by the StyleProfiler connector, editable in the UI, and
    consumed by the ClipDetector and render stages.
    """

    id: str = Field(default_factory=_uid)
    name: str = "Default Style"
    source_handle: Optional[str] = None

    # Clip selection preferences learned from the page.
    target_duration_sec: int = 40
    min_duration_sec: int = 20
    max_duration_sec: int = 90
    hook_style: str = "question"  # question | bold_claim | story | stat
    tone: str = "energetic"

    # Visual defaults.
    aspect_ratio: AspectRatio = AspectRatio.VERTICAL_9_16
    subtitle: SubtitleStyle = Field(default_factory=SubtitleStyle)
    title: TitleStyle = Field(default_factory=TitleStyle)

    # Behaviour toggles.
    auto_zoom: bool = True
    zoom_intensity: float = 1.15
    use_broll: bool = True
    broll_density: float = 0.3  # fraction of clip covered by b-roll

    # Free-form notes / raw analysis payload from the connector.
    notes: str = ""
    raw_analysis: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# --------------------------------------------------------------------------- #
# Clips
# --------------------------------------------------------------------------- #
class Subtitle(BaseModel):
    start_sec: float
    end_sec: float
    text: str


class BrollInsertion(BaseModel):
    start_sec: float
    end_sec: float
    asset_id: str
    source: str = "pexels"  # pexels | storyblocks | local
    url: Optional[str] = None
    query: Optional[str] = None


class ClipTitle(BaseModel):
    text: str
    editable: bool = True


class Clip(BaseModel):
    """A single candidate reel extracted from the source podcast."""

    id: str = Field(default_factory=_uid)
    project_id: str

    # Source window in the original 16:9 podcast.
    source_start_sec: float
    source_end_sec: float

    # Scoring from the clip detector.
    score: float = 0.0
    reason: str = ""

    # Editable creative content.
    title: ClipTitle = Field(default_factory=lambda: ClipTitle(text="Untitled Clip"))
    subtitles: list[Subtitle] = Field(default_factory=list)
    broll: list[BrollInsertion] = Field(default_factory=list)

    # Per-clip overrides (fall back to the project StyleProfile when None).
    subtitle_style: Optional[SubtitleStyle] = None
    title_style: Optional[TitleStyle] = None

    selected: bool = True
    render_job_id: Optional[str] = None

    created_at: datetime = Field(default_factory=_now)

    @property
    def duration_sec(self) -> float:
        return round(self.source_end_sec - self.source_start_sec, 3)


# --------------------------------------------------------------------------- #
# Projects
# --------------------------------------------------------------------------- #
class Project(BaseModel):
    id: str = Field(default_factory=_uid)
    name: str
    instagram_handle: Optional[str] = None

    # Path to the raw 16:9 podcast on the local machine.
    source_video_path: Optional[str] = None
    source_duration_sec: Optional[float] = None

    style_profile_id: Optional[str] = None

    # Stage progress tracking (stage -> JobStatus).
    stage_status: dict[str, JobStatus] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# --------------------------------------------------------------------------- #
# Render jobs
# --------------------------------------------------------------------------- #
class RenderJob(BaseModel):
    id: str = Field(default_factory=_uid)
    project_id: str
    clip_id: str

    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0  # 0.0 - 1.0
    message: str = ""

    output_path: Optional[str] = None
    engine: str = "davinci_resolve"

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# --------------------------------------------------------------------------- #
# Pipeline job (tracks a full run across stages)
# --------------------------------------------------------------------------- #
class StageResult(BaseModel):
    stage: PipelineStage
    status: JobStatus = JobStatus.PENDING
    message: str = ""
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    data: dict[str, Any] = Field(default_factory=dict)


class PipelineJob(BaseModel):
    id: str = Field(default_factory=_uid)
    project_id: str
    status: JobStatus = JobStatus.PENDING
    stages: list[StageResult] = Field(default_factory=list)
    current_stage: Optional[PipelineStage] = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
