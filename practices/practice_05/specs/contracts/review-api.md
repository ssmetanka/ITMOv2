# Review API Contract (v2)

Canonical JSON shapes:

- GET /api/limits -> { "max_lines": 300, "max_chars": 10000 }
- POST /api/reviews { diff: string } -> 200 { id, created_at, status: "success", review }
- GET /api/reviews?limit=N -> { items: [Review], total: int }
- GET /api/reviews/{id} -> Review | 404 { error }

Errors: { error: { code, message, details } } with codes DIFF_EMPTY, DIFF_TOO_LARGE, LLM_UNAVAILABLE, INVALID_REQUEST, NOT_FOUND.

Notes: Limits object is flat. The previously proposed nested limits format {"limits":{...}} is rejected for compatibility. See CONTRACT_DIFF.md.
