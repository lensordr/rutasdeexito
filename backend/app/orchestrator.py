"""
Pipeline orchestrator.

Runs the podcast-to-reels pipeline stage by stage, updating a PipelineJob
with per-stage status. Each stage delegates to a connector resolved from
the registry, so swapping a stub for a real integration requires no change
here. Runs are executed on a background thread so the API stays responsive.
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone

from .connectors.registry import ConnectorRegistry, registry as default_registry
from .models import (
    JobStatus,
    PipelineJob,
    PipelineStage,
    Project,
    StageResult,
    Subtitle,
)
from .store import store


def _now():
    return datetime.now(timezone.utc)


class Orchestrator:
    def __init__(self, reg: ConnectorRegistry | None = None):
        self.reg = reg or default_registry

    def create_job(self, project: Project) -> PipelineJob:
        job = PipelineJob(
            project_id=project.id,
            stages=[StageResult(stage=s) for s in PipelineStage],
        )
        store.pipeline_jobs[job.id] = job
        store.save()
        return job

    def run_async(self, job_id: str) -> None:
        t = threading.Thread(target=self._run, args=(job_id,), daemon=True)
        t.start()

    # ------------------------------------------------------------------ #
    def _set_stage(self, job: PipelineJob, stage: PipelineStage) -> StageResult:
        sr = next(s for s in job.stages if s.stage == stage)
        sr.status = JobStatus.RUNNING
        sr.started_at = _now()
        job.current_stage = stage
        job.updated_at = _now()
        store.save()
        return sr

    def _finish_stage(self, job: PipelineJob, sr: StageResult, msg: str, data=None):
        sr.status = JobStatus.COMPLETED
        sr.finished_at = _now()
        sr.message = msg
        if data:
            sr.data = data
        job.updated_at = _now()
        store.save()

    def _run(self, job_id: str) -> None:
        job = store.pipeline_jobs[job_id]
        project = store.projects[job.project_id]
        job.status = JobStatus.RUNNING
        store.save()

        try:
            # 1. Analyze Instagram
            sr = self._set_stage(job, PipelineStage.ANALYZE_INSTAGRAM)
            reels = self.reg.instagram().fetch_recent_reels(
                project.instagram_handle or "", limit=30
            )
            self._finish_stage(job, sr, f"Fetched {len(reels)} reels",
                               {"reel_count": len(reels)})

            # 2. Build style profile
            sr = self._set_stage(job, PipelineStage.BUILD_STYLE_PROFILE)
            profile = self.reg.style_profiler().build_profile(
                project.instagram_handle or "", reels
            )
            store.style_profiles[profile.id] = profile
            project.style_profile_id = profile.id
            store.save()
            self._finish_stage(job, sr, f"Built style profile '{profile.name}'",
                               {"style_profile_id": profile.id})

            # 3. Transcribe
            sr = self._set_stage(job, PipelineStage.TRANSCRIBE)
            subtitles: list[Subtitle] = self.reg.transcription().transcribe(
                project.source_video_path or "", progress=None
            )
            self._finish_stage(job, sr, f"Transcribed {len(subtitles)} segments",
                               {"segment_count": len(subtitles)})

            # 4. Detect clips
            sr = self._set_stage(job, PipelineStage.DETECT_CLIPS)
            clips = self.reg.clip_detector().detect(project, profile, subtitles)
            for c in clips:
                store.clips[c.id] = c
            store.save()
            self._finish_stage(job, sr, f"Detected {len(clips)} clips",
                               {"clip_ids": [c.id for c in clips]})

            # 5. Fetch b-roll
            sr = self._set_stage(job, PipelineStage.FETCH_BROLL)
            total_broll = 0
            for c in clips:
                c.broll = self.reg.broll().find_broll(c, profile)
                total_broll += len(c.broll)
                store.clips[c.id] = c
            store.save()
            self._finish_stage(job, sr, f"Added {total_broll} b-roll insertions",
                               {"broll_count": total_broll})

            # 6. Render stage is left as PENDING here: rendering is triggered
            #    per-clip from the Render page so the user can review first.
            render_sr = next(
                s for s in job.stages if s.stage == PipelineStage.RENDER
            )
            render_sr.message = "Ready - trigger renders from the Render page."

            job.status = JobStatus.COMPLETED
            job.current_stage = None
            job.updated_at = _now()
            store.save()
        except Exception as exc:  # noqa: BLE001
            job.status = JobStatus.FAILED
            if job.current_stage:
                sr = next(s for s in job.stages if s.stage == job.current_stage)
                sr.status = JobStatus.FAILED
                sr.message = str(exc)
            job.updated_at = _now()
            store.save()


orchestrator = Orchestrator()
