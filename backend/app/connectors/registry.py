"""
Connector registry.

Central place where the app resolves a connector *interface* to a concrete
*implementation*. Today every key maps to a stub. To wire a real
integration later, implement the matching base class and register it here
(or swap via config) - nothing else in the app needs to change.
"""
from __future__ import annotations

from typing import Any

from .base import (
    BaseConnector,
    BrollConnector,
    ClaudeCodeConnector,
    ClipDetectorConnector,
    InstagramConnector,
    RenderConnector,
    StyleProfilerConnector,
    TranscriptionConnector,
)
from . import stubs

# Maps connector key -> (interface, default implementation class).
_IMPLEMENTATIONS: dict[str, type[BaseConnector]] = {
    "instagram": stubs.StubInstagram,
    "style_profiler": stubs.StubStyleProfiler,
    "transcription": stubs.StubTranscription,
    "clip_detector": stubs.StubClipDetector,
    "broll": stubs.StubBroll,
    "render": stubs.StubRender,
    "claude_code": stubs.StubClaudeCode,
}


class ConnectorRegistry:
    def __init__(self, config: dict[str, dict[str, Any]] | None = None):
        self._config = config or {}

    def _resolve_config(self, key: str) -> dict[str, Any]:
        # Pull saved user values (API keys/paths) for this connector.
        try:
            from ..connector_config import connector_config

            return connector_config.raw_values(key)
        except Exception:
            return self._config.get(key, {})

    def get(self, key: str) -> BaseConnector:
        if key not in _IMPLEMENTATIONS:
            raise KeyError(f"Unknown connector: {key}")
        # Build fresh each time so newly-saved config is always picked up.
        impl = _IMPLEMENTATIONS[key]
        return impl(self._resolve_config(key))

    # Typed accessors for orchestrator ergonomics.
    def instagram(self) -> InstagramConnector:
        return self.get("instagram")  # type: ignore[return-value]

    def style_profiler(self) -> StyleProfilerConnector:
        return self.get("style_profiler")  # type: ignore[return-value]

    def transcription(self) -> TranscriptionConnector:
        return self.get("transcription")  # type: ignore[return-value]

    def clip_detector(self) -> ClipDetectorConnector:
        return self.get("clip_detector")  # type: ignore[return-value]

    def broll(self) -> BrollConnector:
        return self.get("broll")  # type: ignore[return-value]

    def render(self) -> RenderConnector:
        return self.get("render")  # type: ignore[return-value]

    def claude_code(self) -> ClaudeCodeConnector:
        return self.get("claude_code")  # type: ignore[return-value]

    def all_status(self) -> list[dict[str, Any]]:
        out = []
        for key in _IMPLEMENTATIONS:
            c = self.get(key)
            status = c.health_check()
            out.append({"key": key, "label": c.label, **status.to_dict()})
        return out


# Module-level singleton used by the app.
registry = ConnectorRegistry()
