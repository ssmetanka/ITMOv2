# Comparison: Spec Kit vs OpenSpec

- Структура спецификаций: OpenSpec — единая схема/контракт; GitHub Spec Kit — набор markdown: spec/plan/tasks/negotiation/analyze.
- Рабочий процесс: OpenSpec — декларативные схемы; Spec Kit — процессная модель с контрольными точками.
- Предложение изменений: OpenSpec — PR к схемам; Spec Kit — CONTRACT_NEGOTIATION.md и CONTRACT_DIFF.md.
- Согласование: OpenSpec — через code review; Spec Kit — явные раунды переговоров и фиксация решений.
- Планирование: OpenSpec — отдельно; Spec Kit — встроенные Plan и Tasks с трассировкой к требованиям.
- Декомпозиция: OpenSpec — разделение по разделам схем; Spec Kit — tasks.md с ID и файлами для правок.
- Реализация: оба не навязывают стек; Spec Kit акцентирует TDD.
- Валидация: OpenSpec — валидаторы схем; Spec Kit — контрактные фикстуры, юнит и E2E тесты.
- Архивирование: OpenSpec — версионирование схем; Spec Kit — v1/v2 и CONTRACT_DIFF.
- Интеграция с AI-агентами: OpenSpec — ограниченная; Spec Kit — через AGENTS.md, Skills, MCP.
