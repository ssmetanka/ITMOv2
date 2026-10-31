#!/bin/sh
set -e
PORT=8000
python -m app.server --port $PORT &
PID=$!
sleep 0.5
echo "== limits =="
curl -s http://localhost:$PORT/api/limits
echo
echo "== create success =="
curl -s -X POST http://localhost:$PORT/api/reviews -d '{"diff":"+ ok"}'
echo
echo "== create empty =="
curl -s -X POST http://localhost:$PORT/api/reviews -d '{"diff":"   "}'
echo
echo "== list =="
curl -s http://localhost:$PORT/api/reviews?limit=5
echo
kill $PID || true
