import unittest
import time
from app.reviewer import ReviewService, MAX_DIFF_LINES

class MockHangingLLM:
    def generate_review(self, diff_text, timeout=2.0):
        time.sleep(timeout + 0.5)
        return "late response"

class TestReviewService(unittest.TestCase):
    def setUp(self):
        self.service = ReviewService()

    # Сценарии Фичи A
    def test_feature_a_valid_diff(self):
        valid_diff = "+ print('hello world')\n" * 10
        res = self.service.review_code(valid_diff)
        self.assertEqual(res["status"], "success")

    def test_feature_a_rejects_oversized_diff(self):
        huge_diff = "+ line\n" * (MAX_DIFF_LINES + 50)
        with self.assertRaises(ValueError) as ctx:
            self.service.review_code(huge_diff)
        self.assertIn("Diff too large", str(ctx.exception))

    def test_feature_a_rejects_empty_diff(self):
        with self.assertRaises(ValueError):
            self.service.review_code("   ")

    # Сценарии Фичи B
    def test_feature_b_handles_llm_timeout(self):
        hanging_service = ReviewService(llm_client=MockHangingLLM(), timeout_sec=0.5)
        valid_diff = "+ const x = 1;"
        with self.assertRaises(RuntimeError) as ctx:
            hanging_service.review_code(valid_diff)
        self.assertIn("LLM service unavailable or timed out", str(ctx.exception))

