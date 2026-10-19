import time

MAX_DIFF_LINES = 300
MAX_DIFF_CHARS = 10000

class ReviewService:
    def __init__(self, llm_client=None, timeout_sec: float = 2.0):
        self.llm_client = llm_client
        self.timeout_sec = timeout_sec

    def validate_diff(self, diff_text: str) -> None:
        """Фича A: проверка размера входящего diff без обращения к LLM."""
        if not diff_text or not diff_text.strip():
            raise ValueError("Diff cannot be empty")
        
        if len(diff_text) > MAX_DIFF_CHARS:
            raise ValueError("Diff too large: character limit exceeded")
            
        lines = diff_text.strip().splitlines()
        if len(lines) > MAX_DIFF_LINES:
            raise ValueError(f"Diff too large: {len(lines)} lines exceeds limit of {MAX_DIFF_LINES}")

    def review_code(self, diff_text: str) -> dict:
        """Основной пайплайн: валидация A -> защищённый вызов LLM B."""
        # 1. Валидация A (ранний отказ)
        self.validate_diff(diff_text)

        # 2. Вызов LLM с контролем таймаута (Фича B)
        start_time = time.time()
        try:
            if self.llm_client:
                # Имитация защищенного вызова
                result = self.llm_client.generate_review(diff_text, timeout=self.timeout_sec)
            else:
                result = "Mock review: code looks solid."
                
            if time.time() - start_time > self.timeout_sec:
                raise TimeoutError("Execution exceeded timeout threshold")
                
            return {"status": "success", "review": result}
        except (TimeoutError, Exception) as err:
            raise RuntimeError(f"LLM service unavailable or timed out: {str(err)}")
