"""
Activity Logging Service
Capture user interactions for debugging/tracking purposes.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

LOG_PATH = Path(__file__).parent.parent / "activity.log"


def _serialize_details(details: Optional[Dict[str, Any]]) -> str:
    """Serialize details dict to a compact JSON string for logging."""
    if not details:
        return "{}"
    try:
        return json.dumps(details, ensure_ascii=True, default=str)
    except TypeError:
        # Fallback: convert non-serializable objects to str
        safe_details = {k: str(v) for k, v in details.items()}
        return json.dumps(safe_details, ensure_ascii=True)


def log_event(category: str, action: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Append a structured log line with timestamp, category and action."""
    timestamp = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
    payload = _serialize_details(details)
    line = f"{timestamp} | {category} | {action} | {payload}\n"

    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception as exc:  # pragma: no cover - logging must not break app
        print(f"[activity_log] Failed to write log: {exc}")
