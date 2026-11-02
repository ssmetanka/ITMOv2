#!/bin/sh
set -eu

PORT=8000
HOST=127.0.0.1

cleanup() {
  if [ -n "${PID:-}" ]; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

python3 -m app.server --port "$PORT" &
PID=$!

# Wait for server readiness
i=0
until curl -s --fail "http://$HOST:$PORT/api/limits" >/dev/null; do
  i=$((i+1))
  if [ "$i" -gt 50 ]; then
    echo "Server did not become ready" >&2
    exit 1
  fi
  sleep 0.1
done

echo "== limits =="
curl -s "http://$HOST:$PORT/api/limits" | jq . || curl -s "http://$HOST:$PORT/api/limits"
echo
echo "== create success =="
curl -s -X POST "http://$HOST:$PORT/api/reviews" -H 'Content-Type: application/json' -d '{"diff":"+ ok\n"}' | jq . || true
echo
echo "== create empty =="
curl -s -X POST "http://$HOST:$PORT/api/reviews" -H 'Content-Type: application/json' -d '{"diff":"   "}' | jq . || true
echo
echo "== create too large =="
LARGE_DIFF=$(python3 - <<'PY'
print('+'*10001)
PY
)
curl -s -X POST "http://$HOST:$PORT/api/reviews" -H 'Content-Type: application/json' -d "{\"diff\":\"$LARGE_DIFF\"}" | jq . || true
echo
echo "== list =="
curl -s "http://$HOST:$PORT/api/reviews?limit=5" | jq . || true
echo
exit 0
