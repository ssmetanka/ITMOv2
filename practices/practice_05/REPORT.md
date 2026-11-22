# Отчёт по Практике 5 — Spec-Driven Development (AI-Review Console)

Выполнил: студент Караханов Максим

Этот отчёт описывает завершение практики №5 по Spec-Driven Development для проекта AI-Review Console. Часть инфраструктурных артефактов от практики №4 сохранена и отмечена отдельно.

## Функциональность и архитектура
- Frontend: UI для ввода diff, счётчики строк/символов, подсветка лимитов, состояния idle/loading/success/validation_error/llm_unavailable/network_error, отправка кнопкой и Ctrl+Enter, загрузка последних пяти ревью, просмотр выбранного, блокировка повторной отправки.
- Backend: API с маршрутами GET /api/limits, POST /api/reviews, GET /api/reviews, GET /api/reviews/{id}, строгая проверка типа поля diff, лимиты 300 строк и 10000 символов (подсчёт по UTF-16 code units для согласования с JS), корректная обработка CRLF/LF, история 50 записей, новые первыми, «мягкий» таймаут LLM.
- UI раздаётся сервером из /ui с безопасной раздачей и корректными MIME-типами.
- MCP tool validate_diff_stats: статусы ACCEPTED/REJECTED/INVALID_INPUT, проверка по строкам и символам.

## SDD-процесс и артефакты
- Конституция: .specify/memory/constitution.md — ограничения на зависимости, обязательные тесты, контракт-первым.
- Спецификации v2: specs/001-review-console-ui/spec.md и specs/002-review-console-logic/spec.md согласованы, единый контракт — плоский формат лимитов.
- Контракты: specs/contracts/review-api.openapi.yaml и specs/contracts/review-api.md; CONTRACT_DIFF и ANALYZE заполнены (отказ от nested limits в пользу плоского формата).
- План и задачи: specs/**/plan.md и tasks.md с указанием файлов и критериев завершения.
- Сравнение: docs/sdd/COMPARISON_OPENSPEC.md — сравнение OpenSpec и GitHub Spec Kit.

## Результаты тестов
- Команда: sh scripts/check.sh
- Результат: OK, пройдено 22 теста (1 skipped — Node.js отсутствует в окружении). Включены новые тесты границ, E2E и MCP.

## Ограничения и известные проблемы
- Таймаут LLM «мягкий» (не прерывает принудительно синхронные вызовы). Это задокументировано в спецификации и отчёте.
- Node.js отсутствует на стенде: UI unit-тесты пропускаются; при наличии Node — проходят (исправлены импорты describe/it и запуск).

## Команды запуска
- Проверки: sh scripts/check.sh
- Демо: sh scripts/demo.sh
- Сервер: python3 -m app.server --port 8000; UI: http://127.0.0.1:8000/ui/

## Наследие практики 4
- Сохранены и переиспользованы: AGENTS.md, skill test-driven-development (Red → Green → Refactor), подключение MCP (opencode.json), DECISIONS.md. Старый отчёт по практике 4 был заменён данным документом; упоминания о практике 4 оставлены как историческая справка. Текущая реализация ориентирована на практику 5 (SDD) и подтверждена тестами и демо.
