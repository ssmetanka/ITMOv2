from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any, Dict, Optional

from app.reviewer import (
    ReviewService,
    MAX_DIFF_CHARS,
    MAX_DIFF_LINES,
    DiffEmptyError,
    DiffTooLargeError,
)
from app.history import HistoryStore


class Api:
    def __init__(self, llm_client=None, timeout_sec: float = 2.0):
        self.history = HistoryStore(capacity=50)
        self.service = ReviewService(llm_client=llm_client, timeout_sec=timeout_sec)

    def get_limits(self) -> Dict[str, int]:
        return {"max_lines": MAX_DIFF_LINES, "max_chars": MAX_DIFF_CHARS}

    def create_review(self, payload: Dict[str, Any]) -> (int, Dict[str, Any]):
        # Strict input validation: must be JSON object with string field 'diff'
        if not isinstance(payload, dict) or "diff" not in payload:
            return self._error(HTTPStatus.BAD_REQUEST, "INVALID_REQUEST", "Missing 'diff' field")
        diff = payload.get("diff")
        if not isinstance(diff, str):
            return self._error(HTTPStatus.BAD_REQUEST, "INVALID_REQUEST", "Field 'diff' must be a string")
        try:
            result = self.service.review_code(diff)
            # success; add to history
            record = self.history.add(result["review"])
            return 200, record
        except DiffEmptyError as e:
            return self._error(HTTPStatus.UNPROCESSABLE_ENTITY, "DIFF_EMPTY", str(e))
        except DiffTooLargeError:
            # Normalize message to "Diff too large"
            return self._error(HTTPStatus.UNPROCESSABLE_ENTITY, "DIFF_TOO_LARGE", "Diff too large")
        except RuntimeError as e:
            # LLM timeout/unavailable; do not add to history
            return self._error(HTTPStatus.GATEWAY_TIMEOUT, "LLM_UNAVAILABLE", "LLM service unavailable or timed out")

    def list_reviews(self, limit: Optional[int]) -> (int, Dict[str, Any]):
        return 200, self.history.list(limit=limit)

    def get_review(self, review_id: str) -> (int, Dict[str, Any]):
        rec = self.history.get(review_id)
        if not rec:
            return self._error(HTTPStatus.NOT_FOUND, "NOT_FOUND", "Review not found")
        return 200, rec

    @staticmethod
    def _error(status: HTTPStatus, code: str, message: str):
        return status, {"error": {"code": code, "message": message, "details": {}}}
