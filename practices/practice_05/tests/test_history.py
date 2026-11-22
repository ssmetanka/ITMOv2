import unittest

from app.history import HistoryStore


class TestHistoryStore(unittest.TestCase):
    def test_ring_capacity_eviction(self):
        store = HistoryStore(capacity=3)
        ids = []
        for i in range(5):
            rec = store.add(f"review {i}")
            ids.append(rec["id"])
        data = store.list()
        self.assertEqual(data["total"], 3)
        # Newest first
        self.assertEqual(len(data["items"]), 3)
        self.assertEqual(data["items"][0]["review"], "review 4")
        # Oldest (review 0,1) must be evicted
        remaining_ids = {it["id"] for it in data["items"]}
        self.assertNotIn(ids[0], remaining_ids)
        self.assertNotIn(ids[1], remaining_ids)

    def test_list_limit(self):
        store = HistoryStore(capacity=5)
        for i in range(4):
            store.add(f"r{i}")
        data = store.list(limit=2)
        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(data["total"], 4)

    def test_get_by_id(self):
        store = HistoryStore(capacity=2)
        rec = store.add("abc")
        found = store.get(rec["id"])
        self.assertIsNotNone(found)
        self.assertEqual(found["review"], "abc")
