"""Small clock abstraction for deterministic tests."""
from datetime import datetime, timezone
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

