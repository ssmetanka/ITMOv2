# CONTRACT NEGOTIATION

Round 1
- Team UI: Предлагаем формат ошибок {error:{code,message,details}} и коды DIFF_EMPTY, DIFF_TOO_LARGE, LLM_UNAVAILABLE, INVALID_REQUEST, NOT_FOUND. История: 5 последних, новые первыми.
- Team Logic: Согласны по формату ошибок; сервер — источник истины лимитов; история хранит до 50 записей, UI запрашивает limit=5.
- Decision: Принято. Сервер считает лимиты, UI получает их через GET /api/limits.

Round 2
- Team UI: Таймаут клиента 5с, сервер 2с. При 504 UI показывает llm_unavailable и кнопку «Повторить».
- Team Logic: Сервер возвращает 504 с code=LLM_UNAVAILABLE. Каждый POST идемпотентности не гарантирует — каждая попытка создаёт новую запись при успехе.
- Decision: Принято. UI ретраи не объединяют записи.

Round 3
- Team UI: Формат success ответа: {id, created_at, status: "success", review}.
- Team Logic: Добавим {limits:{max_lines,max_chars}} в /api/limits; id — строка (uuid-like), created_at — ISO-8601 UTC.
- Decision: Принято. Пустая история → отдельный ответ {items:[], total:0}.

Round 4 (v2 alignment)
- Contradiction: nested limits vs flat limits in OpenAPI and fixtures.
- Decision: Keep flat {max_lines,max_chars} for backward compatibility. Update specs and docs accordingly.
- Additional: Non-string diff yields 400 INVALID_REQUEST.
