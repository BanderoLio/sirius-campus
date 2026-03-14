import asyncio
from datetime import datetime, timezone
from pathlib import Path

from src.config import settings


def _append_line(path: str, line: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as file:
        file.write(line)


async def write_request_audit(endpoint: str, resource_id: str | None, caller: str) -> None:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "resource_id": resource_id,
        "caller": caller,
    }
    line = f"{payload}\n"
    await asyncio.to_thread(_append_line, settings.request_audit_log_file, line)
