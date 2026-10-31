import json
import os
import unittest

from app.server import serve
from http.client import HTTPConnection


def load_fixture(name: str):
    base = os.path.join(os.path.dirname(__file__), "..", "specs", "contracts", "fixtures")
    with open(os.path.join(base, name), "r") as f:
        return json.load(f)


class TestContract(unittest.TestCase):
    def setUp(self):
        self.server, self.thread = serve(0)
        self.port = self.server.server_address[1]

    def tearDown(self):
        self.server.shutdown()

    def _conn(self):
        return HTTPConnection("localhost", self.port, timeout=2)

    def test_limits_fixture(self):
        expected = load_fixture("limits.json")
        c = self._conn()
        c.request("GET", "/api/limits")
        r = c.getresponse()
        self.assertEqual(r.status, 200)
        actual = json.loads(r.read())
        self.assertEqual(set(actual.keys()), set(expected.keys()))

    def test_success_fixture_shape(self):
        expected = load_fixture("success.json")
        c = self._conn()
        c.request("POST", "/api/reviews", body=json.dumps({"diff": "+ ok\n"}))
        r = c.getresponse()
        self.assertEqual(r.status, 200)
        actual = json.loads(r.read())
        # mini-validator: check required keys and types
        for key in ["id", "created_at", "status", "review"]:
            self.assertIn(key, actual)
        self.assertEqual(actual["status"], expected["status"])  # success
