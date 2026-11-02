# Plan (Logic) — v2

1. LG-001 Strict diff type validation. Files: app/api.py. Done: 400 INVALID_REQUEST on non-string.
2. LG-002 UTF-16 char counting and CRLF normalization. Files: app/reviewer.py. Done: splitlines and utf-16 units.
3. LG-003 Soft timeout around LLM call. Files: app/reviewer.py. Done: worker thread join with timeout.
4. LG-004 Serve UI statics. Files: app/server.py. Done: /ui index and static with path traversal guard.
5. LG-005 History capacity/order. Files: app/history.py. Done: ring buffer newest-first, cap 50.
