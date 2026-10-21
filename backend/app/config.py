"""Application configuration loaded from environment / .env."""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # dotenv optional
    pass


BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
DATA_DIR = Path(os.getenv("REELFORGE_DATA_DIR", BASE_DIR / "data"))
OUTPUT_DIR = Path(os.getenv("REELFORGE_OUTPUT_DIR", BASE_DIR / "output"))

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    app_name: str = "ReelForge"
    version: str = "0.1.0"

    data_dir: Path = DATA_DIR
    output_dir: Path = OUTPUT_DIR

    # CORS origins for the local Vite dev server.
    cors_origins: list[str] = [
        o.strip()
        for o in os.getenv(
            "REELFORGE_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
    ]

    host: str = os.getenv("REELFORGE_HOST", "127.0.0.1")
    port: int = int(os.getenv("REELFORGE_PORT", "8000"))


settings = Settings()
