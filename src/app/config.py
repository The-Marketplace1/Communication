"""Runtime configuration with safe local defaults."""
from __future__ import annotations
import os
from dataclasses import dataclass
@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8080"))
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8080")
settings = Settings()

