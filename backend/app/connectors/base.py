"""
Connector interface contracts.

Every external integration (Instagram, transcription, clip detection,
b-roll sourcing, DaVinci Resolve rendering, Claude Code) is expressed as
an abstract base class here. The app only ever depends on these
interfaces, never on a concrete implementation. Concrete stubs live in
``connectors/stubs.py``; real implementations can be dropped in later and
selected via the connector registry without touching the rest of the app.
"""
from __future__ import annotations

import abc
from typing import Any, Callable, Optional

from ..models import (
    BrollInsertion,
    Clip,
    Project,
    StyleProfile,
    Subtitle,
)

# A progress callback: (fraction 0..1, human-readable message) -> None
ProgressCB = Callable[[float, str], None]


class ConnectorStatus:
    """Lightweight status descriptor returned by ``health_check``."""

    def __init__(
        self,
        connected: bool,
        detail: str = "",
        is_stub: bool = True,
        configured: bool = False,
    ):
        self.connected = connected
        self.detail = detail
        self.is_stub = is_stub
        self.configured = configured

    def to_dict(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "detail": self.detail,
            "is_stub": self.is_stub,
            "configured": self.configured,
        }


class TestResult:
    """Result of a connector connection test."""

    def __init__(self, ok: bool, message: str):
        self.ok = ok
        self.message = message

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "message": self.message}


class BaseConnector(abc.ABC):
    """Common surface for every connector."""

    #: Stable identifier used in the registry and the UI (e.g. "instagram").
    key: str = "base"
    #: Human-facing label.
    label: str = "Base Connector"

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

    @abc.abstractmethod
    def health_check(self) -> ConnectorStatus:
        """Report whether the connector is configured and reachable."""

    def test_connection(self) -> TestResult:
        """Test using current config. Default derives from ``health_check``.

        Real connectors should override this to make an actual call
        (e.g. a lightweight API ping)."""
        status = self.health_check()
        if status.is_stub:
            if status.configured:
                return TestResult(
                    True,
                    "Configured. (Stub - no real call made yet; this will "
                    "perform a live check once the integration is wired.)",
                )
            return TestResult(
                False, "Not configured. Enter the required fields and save."
            )
        return TestResult(status.connected, status.detail)


class InstagramConnector(BaseConnector):
    """Pulls the user's existing reels/posts for analysis."""

    key = "instagram"
    label = "Instagram (Business/Graph API)"

    @abc.abstractmethod
    def fetch_recent_reels(self, handle: str, limit: int = 30) -> list[dict[str, Any]]:
        """Return metadata for recent reels (captions, durations, metrics...)."""


class StyleProfilerConnector(BaseConnector):
    """Turns raw Instagram data into a StyleProfile (the reel guide)."""

    key = "style_profiler"
    label = "Style Profiler"

    @abc.abstractmethod
    def build_profile(
        self, handle: str, reels: list[dict[str, Any]]
    ) -> StyleProfile:
        """Analyze reels and synthesize a personalized StyleProfile."""


class TranscriptionConnector(BaseConnector):
    """Transcribes the source podcast to timed subtitles."""

    key = "transcription"
    label = "Transcription"

    @abc.abstractmethod
    def transcribe(
        self, video_path: str, progress: Optional[ProgressCB] = None
    ) -> list[Subtitle]:
        """Return a list of timed subtitle segments for the whole source."""


class ClipDetectorConnector(BaseConnector):
    """Finds the best candidate clips in a long transcript."""

    key = "clip_detector"
    label = "Clip Detector"

    @abc.abstractmethod
    def detect(
        self,
        project: Project,
        style: StyleProfile,
        subtitles: list[Subtitle],
        progress: Optional[ProgressCB] = None,
    ) -> list[Clip]:
        """Return scored candidate clips honoring the StyleProfile."""


class BrollConnector(BaseConnector):
    """Sources b-roll footage for a clip (Pexels / Storyblocks / local)."""

    key = "broll"
    label = "B-roll (Pexels/Storyblocks)"

    @abc.abstractmethod
    def find_broll(
        self, clip: Clip, style: StyleProfile
    ) -> list[BrollInsertion]:
        """Return b-roll insertions suggested for the given clip."""


class RenderConnector(BaseConnector):
    """Renders a 9:16 reel. Default engine: DaVinci Resolve Studio."""

    key = "render"
    label = "DaVinci Resolve Studio"

    @abc.abstractmethod
    def render_clip(
        self,
        project: Project,
        clip: Clip,
        style: StyleProfile,
        output_dir: str,
        progress: Optional[ProgressCB] = None,
    ) -> str:
        """Render the clip and return the output file path."""


class ClaudeCodeConnector(BaseConnector):
    """Optional AI assist: title/hook generation, editing suggestions."""

    key = "claude_code"
    label = "Claude Code"

    @abc.abstractmethod
    def suggest_titles(self, clip: Clip, style: StyleProfile) -> list[str]:
        """Return title/hook suggestions for a clip."""
