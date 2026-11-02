import unittest
import json

from service import Shop


class SecurityRegressionTest(unittest.TestCase):
    def setUp(self):
        self.shop = Shop()
        self.addCleanup(self.shop.close)

    def request(self, method, path, body=None, headers=None):
        with self.shop.lock:
            return self.shop.dispatch(method, path, body or {}, headers or {})

    def login(self, username="alice", password="learn-alice"):
        status, result = self.request("POST", "/login", {"username": username, "password": password})
        self.assertEqual(status, 200)
        return {"X-Token": result["token"]}

    def test_fix_F01_profile_idor_and_injection(self):
        alice = self.login()
        status, rows = self.request("GET", "/profile?id=2", headers=alice)
        self.assertEqual(status, 200)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], 1)

        status, rows = self.request("GET", "/profile?id=1 OR 1=1", headers=alice)
        self.assertEqual(status, 200)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], 1)

    def test_fix_F04_orders_listing_scoped(self):
        alice = self.login()
        status, orders = self.request("GET", "/orders", headers=alice)
        self.assertEqual(status, 200)
        self.assertTrue(all(o["owner"] == 1 for o in orders))

    def test_fix_F05_catalog_price_enforced(self):
        alice = self.login()
        status, order = self.request("POST", "/orders", {"product": "lamp", "price": 1}, headers=alice)
        self.assertEqual(status, 201)
        self.assertEqual(order["price"], 1500)

    def test_fix_F06_admin_export_requires_staff_session(self):
        status, _ = self.request("GET", "/admin/export", headers={"X-Role": "staff"})
        self.assertEqual(status, 401)

        alice = {**self.login(), "X-Role": "staff"}
        status, _ = self.request("GET", "/admin/export", headers=alice)
        self.assertEqual(status, 403)

    def test_fix_F07_files_enforce_user_scope(self):
        alice = self.login()
        status, data = self.request("GET", "/files?user=alice&path=receipt.txt", headers=alice)
        self.assertEqual(status, 200)
        self.assertIn("TEST_ALICE", data["content"]) 

        status, _ = self.request("GET", "/files?user=bob&path=receipt.txt", headers=alice)
        self.assertIn(status, (403, 404))

        status, _ = self.request("GET", "/files?user=alice&path=../private/operator-note.txt", headers=alice)
        self.assertIn(status, (400, 403, 404))

    def test_fix_F09_assistant_execute_scoped_tools(self):
        alice = self.login()
        status, _ = self.request(
            "POST", 
            "/assistant/execute", 
            {"decision": {"tool": "read_file", "arguments": {"path": "private/operator-note.txt"}}}, 
            headers=alice,
        )
        self.assertIn(status, (403, 400))

        status, _ = self.request(
            "POST",
            "/assistant/execute",
            {"decision": {"tool": "export_profiles", "arguments": {}}},
            headers=alice,
        )
        self.assertEqual(status, 403)

        status, _ = self.request(
            "POST",
            "/assistant/execute",
            {"decision": {"tool": "delete_tree", "arguments": {"path": "."}}},
            headers=alice,
        )
        self.assertEqual(status, 403)

    def test_fix_F12_logs_protected(self):
        alice = self.login()
        status, _ = self.request("GET", "/debug/logs", headers=alice)
        self.assertIn(status, (401, 403))

    def test_assistant_context_requires_auth_and_owner_scope(self):
        # no token
        status, _ = self.request("GET", "/assistant/context?order_id=1")
        self.assertEqual(status, 401)
        # invalid token
        status, _ = self.request("GET", "/assistant/context?order_id=1", headers={"X-Token": "bad"})
        self.assertEqual(status, 401)
        # alice can read own order
        alice = self.login()
        status, data = self.request("GET", "/assistant/context?order_id=1", headers=alice)
        self.assertEqual(status, 200)
        self.assertIn("chair", data["prompt"])  # order 1 is chair for owner 1
        # alice cannot read bob's order
        status, _ = self.request("GET", "/assistant/context?order_id=2", headers=alice)
        self.assertEqual(status, 404)
        # SQL injection attempts are rejected
        status, _ = self.request("GET", "/assistant/context?order_id=1 OR 1=1", headers=alice)
        self.assertEqual(status, 400)
        status, _ = self.request("GET", "/assistant/context?order_id=1;DROP TABLE orders", headers=alice)
        self.assertEqual(status, 400)
        # missing order_id
        status, _ = self.request("GET", "/assistant/context", headers=alice)
        self.assertEqual(status, 400)
        # bad types
        status, _ = self.request("GET", "/assistant/context?order_id=abc", headers=alice)
        self.assertEqual(status, 400)

    def test_reviews_xss_escaped_and_auth_required(self):
        # anonymous cannot post
        status, _ = self.request("POST", "/reviews", {"product": "chair", "text": "ok"})
        self.assertEqual(status, 401)
        alice = self.login()
        # special chars
        text = "<script>alert('x')</script> <b onclick=alert(1)>bold</b> & \"quotes\""
        status, _ = self.request("POST", "/reviews", {"product": "chair", "text": text}, headers=alice)
        self.assertEqual(status, 201)
        status, html = self.request("GET", "/reviews/view", headers=alice)
        self.assertEqual(status, 200)
        page = html
        self.assertIn("&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;", page)
        self.assertIn("&lt;b onclick=alert(1)&gt;bold&lt;/b&gt;", page)
        self.assertIn("&amp;", page)
        self.assertIn("&quot;quotes&quot;", page)

    def test_logs_do_not_leak_passwords_or_tokens(self):
        # Login as alice
        status, result = self.request("POST", "/login", {"username": "alice", "password": "learn-alice"})
        self.assertEqual(status, 200)
        token = result["token"]
        # Do a GET and POST to generate logs
        _ = self.request("GET", "/profile", headers={"X-Token": token})
        _ = self.request("POST", "/orders", {"product": "lamp"}, headers={"X-Token": token})
        # Staff retrieves logs
        staff = self.login("staff", "learn-staff")
        status, logs = self.request("GET", "/debug/logs", headers=staff)
        self.assertEqual(status, 200)
        # Check masking
        joined = json.dumps(logs)
        self.assertNotIn("learn-alice", joined)
        self.assertNotIn(token, joined)
        # Sensitive headers should be masked
        for entry in logs:
            headers = entry.get("headers", {})
            if "X-Token" in headers:
                self.assertEqual(headers["X-Token"], "***")
        
    def test_delete_tree_disabled(self):
        staff = self.login("staff", "learn-staff")
        status, result = self.request(
            "POST", 
            "/assistant/execute", 
            {"decision": {"tool": "delete_tree", "arguments": {"path": "."}}}, 
            headers=staff,
        )
        self.assertEqual(status, 403)
        self.assertIn("disabled", result["error"]) 


if __name__ == "__main__":
    unittest.main()
