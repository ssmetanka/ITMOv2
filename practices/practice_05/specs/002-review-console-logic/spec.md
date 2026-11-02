# Review Console Logic — v2

## User Stories
- US-1: Как система, я хочу предоставлять API для ревью и истории, чтобы UI мог работать.

## Functional Requirements
- FR-API-001: GET /api/limits возвращает лимиты MAX_DIFF_LINES, MAX_DIFF_CHARS (плоский формат).
- FR-API-002: POST /api/reviews {diff: string} вызывает ReviewService.review_code; строгая проверка типа.
- FR-API-003: GET /api/reviews?limit=N возвращает историю (новые первыми), максимум 50 хранится.
- FR-API-004: GET /api/reviews/{id} возвращает запись.
- FR-API-005: Исключения типов DiffEmptyError и DiffTooLargeError в reviewer.py с теми же текстами.
- FR-API-006: Таймаут LLM → HTTP 504 с кодом LLM_UNAVAILABLE; валидация → 422; несуществующий id → 404; битый JSON → 400.

## Scenarios
- S-1: Given валидный diff When POST Then success запись создаётся.
- S-2: Given пустой diff When POST Then 422 DIFF_EMPTY.
- S-3: Given слишком большой diff When POST Then 422 DIFF_TOO_LARGE.
- S-4: Given зависание LLM When POST Then 504 LLM_UNAVAILABLE и запись не создаётся.
- S-5: Given неизвестный id When GET Then 404 NOT_FOUND.

## Edge Cases
- Ровно на лимите — success; 301 строк — 422; 10001 символ — 422.

## Success Criteria
- Старые тесты остаются зелёными; API тесты зелёные; контрактные тесты зелёные.

## Out of Scope
- Нет БД, нет auth, только stdlib.

## Допущения об интерфейсе с другой командой
- UI считает строки идентично серверу: diff.strip().splitlines(); лимиты берёт из /api/limits (плоский формат); формат ответов см. контракт.
