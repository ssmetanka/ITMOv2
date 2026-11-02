import unittest

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


if __name__ == "__main__":
    unittest.main()
