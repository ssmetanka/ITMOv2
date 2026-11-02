# CONTRACT DIFF (v1→v2)

- GET /api/limits
  v1: { max_lines, max_chars } flat
  v2: unchanged; flat retained. Decision: reject nested { limits: {...} } for backward compatibility.

- POST /api/reviews
  v1: accepts { diff: string }, errors on validation 422, LLM timeout 504
  v2: unchanged; clarify that diff must be string (type check), non-string is 400 INVALID_REQUEST.

- GET /api/reviews, /api/reviews/{id}
  v1: list { items, total }, record { id, created_at, status, review }
  v2: unchanged; ordering newest-first clarified; list limit param optional; history capacity 50 clarified.

- Error contract
  v1: { error: { code, message, details } }
  v2: unchanged; codes enumerated explicitly.
