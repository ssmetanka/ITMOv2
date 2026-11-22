Завершение практики №6 — AI Testing, Threat Modeling и Security

Ключевые изменения:
- /assistant/context: обязательная авторизация, параметризованный SQL, скоуп владельца, сокрытие чужих заказов.
- /reviews: авторизация на POST, валидация и длина; /reviews/view экранирует HTML (html.escape).
- Безопасные логи: маскирование паролей, токенов, Authorization/Cookie и чувствительных query.
- /assistant/execute: строгая JSON‑схема; delete_tree отключён.
- Обработка ошибок: унифицированный 500 с request_id без утечек внутренних деталей.
- Makefile: единая цель step6, .PHONY обновлён.

Тесты:
- Добавлены регрессии для /assistant/context, XSS, логов, delete_tree и HTTP‑XSS отображения.
- Все тесты: 28 PASS; step6: 4 PASS.

Документы:
- Обновлены threat-model.md/mmd; добавлены docs/SECURITY_AUDIT_BASELINE.md, docs/FINDINGS_REGISTER.md.

Ограничения:
- LLM‑судья не интегрирован как онлайн сервис; защита реализована серверной валидацией и песочницей.
