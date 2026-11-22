"""Exercise the real HTTP transport without an LLM or third-party packages."""

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from service import Shop, make_handler


class HttpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shop = Shop()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.shop))
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()
        cls.shop.close()

    def call(self, method, path, body=None, headers=None):
        headers = {"Content-Type": "application/json", **(headers or {})}
        request = Request(self.base + path, data=json.dumps(body).encode() if body is not None else None,
                          headers=headers, method=method)
        try:
            response = urlopen(request, timeout=5)
        except HTTPError as exc:
            response = exc
        with response:
            return response.status, response.headers, response.read().decode()

    def test_login_and_purchase_over_http(self):
        status, _, body = self.call("POST", "/login", {"username": "alice", "password": "learn-alice"})
        self.assertEqual(status, 200)
        token = json.loads(body)["token"]
        status, headers, body = self.call("POST", "/orders", {"product": "chair"}, {"X-Token": token})
        self.assertEqual(status, 201)
        self.assertIn("application/json", headers["Content-Type"])
        self.assertEqual(json.loads(body)["price"], 5000)

    def test_health_and_not_found(self):
        status, _, body = self.call("GET", "/health")
        self.assertEqual((status, json.loads(body)), (200, {"status": "ok"}))
        self.assertEqual(self.call("GET", "/missing")[0], 404)

    def test_transport_only_binds_loopback(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")

    def test_reviews_are_escaped_over_http(self):
        # login
        status, _, body = self.call("POST", "/login", {"username": "alice", "password": "learn-alice"})
        self.assertEqual(status, 200)
        token = json.loads(body)["token"]
        # post review
        text = "<img src=x onerror=alert(1)> & <script>boom</script>"
        status, _, _ = self.call("POST", "/reviews", {"product": "chair", "text": text}, {"X-Token": token})
        self.assertEqual(status, 201)
        # view reviews
        status, headers, body = self.call("GET", "/reviews/view", headers={"X-Token": token})
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn("&lt;img src=x onerror=alert(1)&gt; &amp; &lt;script&gt;boom&lt;/script&gt;", body)

    def test_assistant_context_http_auth_and_sqli(self):
        # no token
        status, _, _ = self.call("GET", "/assistant/context?order_id=1")
        self.assertEqual(status, 401)
        # login as alice
        status, _, body = self.call("POST", "/login", {"username": "alice", "password": "learn-alice"})
        self.assertEqual(status, 200)
        token = json.loads(body)["token"]
        # own order ok
        status, _, body = self.call("GET", "/assistant/context?order_id=1", headers={"X-Token": token})
        self.assertEqual(status, 200)
        self.assertIn("chair", body)
        # foreign order hidden
        status, _, _ = self.call("GET", "/assistant/context?order_id=2", headers={"X-Token": token})
        self.assertEqual(status, 404)
        # SQLi attempt rejected
        status, _, _ = self.call("GET", "/assistant/context?order_id=1%20OR%201%3D1", headers={"X-Token": token})
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
