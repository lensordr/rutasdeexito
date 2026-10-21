"""
Connector configuration service.

Defines the editable fields for every connector (API keys, tokens, paths),
persists user-entered values to a **gitignored, per-machine** JSON file
(``backend/data/connector_config.json``), and masks secret values before
they are ever returned to the frontend.

GitHub safety:
    * The storage file lives under ``backend/data/`` which is gitignored.
    * Secret values are never echoed back to the browser (only a masked
      placeholder and a ``has_value`` flag).
    * Values are read server-side only when a connector actually runs.
"""
from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .config import settings


@dataclass
class ConnectorField:
    key: str
    label: str
    secret: bool = False
    required: bool = True
    placeholder: str = ""
    help: str = ""

    def to_schema(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "secret": self.secret,
            "required": self.required,
            "placeholder": self.placeholder,
            "help": self.help,
        }


@dataclass
class ConnectorSchema:
    key: str
    label: str
    description: str
    fields: list[ConnectorField] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Field definitions per connector. Extend here as integrations get richer.
# --------------------------------------------------------------------------- #
SCHEMAS: dict[str, ConnectorSchema] = {
    "instagram": ConnectorSchema(
        key="instagram",
        label="Instagram (Business/Graph API)",
        description="Analyze your page's existing reels.",
        fields=[
            ConnectorField("business_account_id", "Business Account ID",
                           secret=False, placeholder="178414..."),
            ConnectorField("access_token", "Access Token", secret=True,
                           placeholder="EAAG...",
                           help="Long-lived token from your Meta app."),
        ],
    ),
    "style_profiler": ConnectorSchema(
        key="style_profiler",
        label="Style Profiler",
        description="Builds your reel creation guide. Runs locally; no keys needed.",
        fields=[],
    ),
    "transcription": ConnectorSchema(
        key="transcription",
        label="Transcription",
        description="Transcribe the podcast to timed subtitles.",
        fields=[
            ConnectorField("provider", "Provider", secret=False, required=False,
                           placeholder="whisper_local | openai",
                           help="Use 'whisper_local' for free local, or 'openai'."),
            ConnectorField("openai_api_key", "OpenAI API Key", secret=True,
                           required=False, placeholder="sk-...",
                           help="Only needed if provider = openai."),
        ],
    ),
    "clip_detector": ConnectorSchema(
        key="clip_detector",
        label="Clip Detector",
        description="Finds the best clips. Can optionally use an LLM.",
        fields=[
            ConnectorField("anthropic_api_key", "Anthropic API Key", secret=True,
                           required=False, placeholder="sk-ant-...",
                           help="Optional: smarter clip selection via Claude."),
        ],
    ),
    "broll": ConnectorSchema(
        key="broll",
        label="B-roll (Pexels/Storyblocks)",
        description="Source stock footage for clips.",
        fields=[
            ConnectorField("pexels_api_key", "Pexels API Key", secret=True,
                           required=False, placeholder="563492..."),
            ConnectorField("storyblocks_api_key", "Storyblocks API Key",
                           secret=True, required=False),
            ConnectorField("storyblocks_api_secret", "Storyblocks API Secret",
                           secret=True, required=False),
        ],
    ),
    "render": ConnectorSchema(
        key="render",
        label="DaVinci Resolve Studio",
        description="Render 9:16 reels locally via DaVinci Resolve.",
        fields=[
            ConnectorField(
                "resolve_script_api", "Resolve Scripting API path", secret=False,
                placeholder=r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting",
                help="Folder set by the Resolve installer."),
            ConnectorField(
                "resolve_script_lib", "fusionscript.dll path", secret=False,
                placeholder=r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"),
        ],
    ),
    "claude_code": ConnectorSchema(
        key="claude_code",
        label="Claude Code",
        description="AI assist for titles, hooks and editing suggestions.",
        fields=[
            ConnectorField("anthropic_api_key", "Anthropic API Key", secret=True,
                           placeholder="sk-ant-..."),
        ],
    ),
}

MASK = "••••••••"


class ConnectorConfigService:
    def __init__(self, path: Optional[Path] = None):
        self._path = path or (settings.data_dir / "connector_config.json")
        self._lock = threading.RLock()
        self._data: dict[str, dict[str, str]] = {}
        self._load()

    # ------------------------------ persistence ----------------------------- #
    def _load(self) -> None:
        if self._path.exists():
            try:
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
            except Exception:
                self._data = {}

    def _save(self) -> None:
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
        tmp.replace(self._path)

    # -------------------------------- reads ---------------------------------- #
    def raw_values(self, connector_key: str) -> dict[str, str]:
        """Server-side only: the real values a connector needs to run."""
        return dict(self._data.get(connector_key, {}))

    def get_value(self, connector_key: str, field_key: str) -> Optional[str]:
        return self._data.get(connector_key, {}).get(field_key)

    def masked_values(self, connector_key: str) -> dict[str, Any]:
        """Safe for the browser: secrets become a mask + has_value flag."""
        schema = SCHEMAS.get(connector_key)
        stored = self._data.get(connector_key, {})
        out: dict[str, Any] = {}
        if not schema:
            return out
        for f in schema.fields:
            val = stored.get(f.key, "")
            has = bool(val)
            if f.secret:
                out[f.key] = {"has_value": has, "display": MASK if has else ""}
            else:
                out[f.key] = {"has_value": has, "display": val}
        return out

    def is_configured(self, connector_key: str) -> bool:
        """True when all *required* fields have a value."""
        schema = SCHEMAS.get(connector_key)
        if not schema:
            return False
        stored = self._data.get(connector_key, {})
        required = [f for f in schema.fields if f.required]
        if not required:
            return True  # connectors with no required fields are always ready
        return all(stored.get(f.key) for f in required)

    # -------------------------------- writes --------------------------------- #
    def save_values(self, connector_key: str, values: dict[str, str]) -> None:
        """Persist values. Empty strings clear a field; the MASK is ignored
        so re-saving a form without re-typing a secret keeps the old value."""
        schema = SCHEMAS.get(connector_key)
        if not schema:
            raise KeyError(f"Unknown connector: {connector_key}")
        with self._lock:
            current = self._data.get(connector_key, {})
            for f in schema.fields:
                if f.key not in values:
                    continue
                incoming = (values[f.key] or "").strip()
                if f.secret and incoming == MASK:
                    continue  # unchanged masked secret - keep existing
                if incoming == "":
                    current.pop(f.key, None)
                else:
                    current[f.key] = incoming
            self._data[connector_key] = current
            self._save()

    def schema_dict(self, connector_key: str) -> dict[str, Any]:
        schema = SCHEMAS[connector_key]
        return {
            "key": schema.key,
            "label": schema.label,
            "description": schema.description,
            "fields": [f.to_schema() for f in schema.fields],
        }


connector_config = ConnectorConfigService()
