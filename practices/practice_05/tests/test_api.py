import json
import threading
import time
import unittest
from http.client import HTTPConnection

from app.server import serve


class HangingLLM:
    def generate_review(self, diff_text, timeout=2.0):
        time.sleep(timeout + 0.5)
        return "late"


class TestApi(unittest.TestCase):
    def setUp(self):
        # start server on port 0 -> choose random free port
        self.server, self.thread = serve(0)
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()

    def _conn(self):
        return HTTPConnection("localhost", self.port, timeout=2)

    def test_limits(self):
        c = self._conn()
        c.request("GET", "/api/limits")
        r = c.getresponse()
        self.assertEqual(r.status, 200)
        data = json.loads(r.read())
        self.assertIn("max_lines", data)
        self.assertIn("max_chars", data)

    def test_create_success_and_history(self):
        c = self._conn()
        payload = {"diff": "+ ok\n"}
        c.request("POST", "/api/reviews", body=json.dumps(payload))
        r = c.getresponse()
        self.assertEqual(r.status, 200)
        data = json.loads(r.read())
        self.assertEqual(data["status"], "success")
        # now list
        c.request("GET", "/api/reviews?limit=5")
        r = c.getresponse()
        self.assertEqual(r.status, 200)
        listing = json.loads(r.read())
        self.assertGreaterEqual(listing["total"], 1)

    def test_validation_errors(self):
        c = self._conn()
        # empty
        c.request("POST", "/api/reviews", body=json.dumps({"diff": "   "}))
        r = c.getresponse()
        self.assertEqual(r.status, 422)
        err = json.loads(r.read())
        self.assertEqual(err["error"]["code"], "DIFF_EMPTY")

    def test_invalid_json(self):
        c = self._conn()
        c.request("POST", "/api/reviews", body="not json")
        r = c.getresponse()
        self.assertEqual(r.status, 400)

    def test_not_found(self):
        c = self._conn()
        c.request("GET", "/api/reviews/nonexistent")
        r = c.getresponse()
        self.assertEqual(r.status, 404)
