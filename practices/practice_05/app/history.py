from __future__ import annotations

import threading
import time
import uuid
from typing import Any, Dict, List, Optional


class HistoryStore:
    """Thread-safe ring buffer for last N review records."""

    def __init__(self, capacity: int = 50):
        self._capacity = capacity
        self._lock = threading.Lock()
        self._items: List[Dict[str, Any]] = []

    def add(self, review_text: str) -> Dict[str, Any]:
        now = time.gmtime()
        created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", now)
        record = {
            "id": str(uuid.uuid4()),
            "created_at": created_at,
            "status": "success",
            "review": review_text,
        }
        with self._lock:
            self._items.insert(0, record)
            if len(self._items) > self._capacity:
                self._items.pop()
        return record

    def list(self, limit: Optional[int] = None) -> Dict[str, Any]:
        with self._lock:
            items = list(self._items)
        if limit is not None:
            items = items[: max(0, int(limit))]
        return {"items": items, "total": len(self._items)}

    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            for it in self._items:
                if it["id"] == item_id:
                    return it
        return None
