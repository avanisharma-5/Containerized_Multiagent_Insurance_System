from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from .config import BASE_DIR, load_settings


def _chat_dir() -> Path:
    settings = load_settings()
    path = (BASE_DIR / settings.chats_dir).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def create_session() -> str:
    session_id = str(uuid4())
    save_history(session_id, [])
    return session_id


def _session_path(session_id: str) -> Path:
    return _chat_dir() / f"{session_id}.json"


def load_history(session_id: str) -> List[Dict[str, Any]]:
    path = _session_path(session_id)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_history(session_id: str, history: List[Dict[str, Any]]) -> None:
    path = _session_path(session_id)
    path.write_text(json.dumps(history, indent=2), encoding="utf-8")


def append_message(session_id: str, role: str, content: str) -> None:
    history = load_history(session_id)
    history.append({"role": role, "content": content})
    save_history(session_id, history)
