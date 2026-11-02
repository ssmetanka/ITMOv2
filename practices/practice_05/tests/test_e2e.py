import json
import subprocess
import sys
import time
import unittest
from http.client import HTTPConnection

class TestE2E(unittest.TestCase):
    def test_end_to_end_flow(self):
        # Start server on random port
        proc = subprocess.Popen([sys.executable, '-m', 'app.server', '--port', '0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            # Give it a moment to bind; no port is printed, so we connect to default 8000 won't work.
            # Instead, spin up a second server via serve() is not possible here; we rely on HTTPConnection retries.
            # Poll a range of likely ports is brittle; instead, stop using subprocess and use in-process serve()?
            # Keep subprocess approach but fetch port via /api/limits on 127.0.0.1:8000 fallback.
            # To make this reliable, run an in-process server.
            proc.terminate()
            proc.wait(timeout=5)
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)

        # In-process server for reliable port discovery
        from app.server import serve
        server, thread = serve(0)
        port = server.server_address[1]
        try:
            c = HTTPConnection('127.0.0.1', port, timeout=2)
            # 1) UI index
            c.request('GET', '/ui/index.html')
            r = c.getresponse(); self.assertEqual(r.status, 200); r.read()
            # 2) limits
            c.request('GET', '/api/limits')
            r = c.getresponse(); self.assertEqual(r.status, 200)
            limits = json.loads(r.read()); self.assertIn('max_lines', limits)
            # 3) send diff
            c.request('POST', '/api/reviews', body=json.dumps({'diff': '+ ok\n'}))
            r = c.getresponse(); self.assertEqual(r.status, 200)
            created = json.loads(r.read()); self.assertEqual(created['status'], 'success')
            rid = created['id']
            # 4) list history
            c.request('GET', '/api/reviews?limit=5')
            r = c.getresponse(); self.assertEqual(r.status, 200)
            listing = json.loads(r.read()); self.assertGreaterEqual(listing['total'], 1)
            # 5) get by id
            c.request('GET', f'/api/reviews/{rid}')
            r = c.getresponse(); self.assertEqual(r.status, 200)
            byid = json.loads(r.read()); self.assertEqual(byid['id'], rid)
        finally:
            server.shutdown()
