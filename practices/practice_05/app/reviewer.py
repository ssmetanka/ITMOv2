import time
import threading


class DiffEmptyError(ValueError):
    pass

class DiffTooLargeError(ValueError):
    pass

MAX_DIFF_LINES = 300
MAX_DIFF_CHARS = 10000

class ReviewService:
    def __init__(self, llm_client=None, timeout_sec: float = 2.0):
        self.llm_client = llm_client
        self.timeout_sec = timeout_sec

    def _utf16_code_units(self, text: str) -> int:
        """Count characters as UTF-16 code units to align with JS String.length."""
        # utf-16-le has no BOM; each code unit is 2 bytes
        return len(text.encode('utf-16-le')) // 2

    def validate_diff(self, diff_text: str) -> None:
        """Фича A: проверка размера входящего diff без обращения к LLM."""
        if not diff_text or not diff_text.strip():
            # Сохраняем текст сообщения для совместимости тестов
            raise DiffEmptyError("Diff cannot be empty")
        
        # Count by UTF-16 code units for parity with frontend
        if self._utf16_code_units(diff_text) > MAX_DIFF_CHARS:
            # Сохраняем текст, который ожидают старые тесты
            raise DiffTooLargeError("Diff too large: character limit exceeded")
        
        lines = diff_text.strip().splitlines()
        if len(lines) > MAX_DIFF_LINES:
            raise DiffTooLargeError(
                f"Diff too large: {len(lines)} lines exceeds limit of {MAX_DIFF_LINES}"
            )

    def review_code(self, diff_text: str) -> dict:
        """Основной пайплайн: валидация A -> защищённый вызов LLM B."""
        # 1. Валидация A (ранний отказ)
        self.validate_diff(diff_text)

        # 2. Вызов LLM с контролем таймаута (Фича B)
        # Implement soft timeout: run client call in a worker thread, wait with timeout.
        # We cannot preemptively abort a blocking call, but we will stop waiting and report timeout.
        result_holder = {"value": None, "error": None}

        def _call():
            try:
                if self.llm_client:
                    result_holder["value"] = self.llm_client.generate_review(diff_text, timeout=self.timeout_sec)
                else:
                    result_holder["value"] = "Mock review: code looks solid."
            except Exception as e:  # capture client errors
                result_holder["error"] = e

        t = threading.Thread(target=_call, daemon=True)
        t.start()
        t.join(self.timeout_sec)
        if t.is_alive():
            # Timed out
            raise RuntimeError("LLM service unavailable or timed out: timeout exceeded")
        if result_holder["error"] is not None:
            raise RuntimeError(f"LLM service unavailable or timed out: {result_holder['error']}")
        return {"status": "success", "review": result_holder["value"]}
