# SDD README

Этот раздел фиксирует артефакты Spec-Driven Development (SDD) для AI-Review Console.

- Конституция: .specify/memory/constitution.md
- Спецификации: specs/001-review-console-ui/spec.md (UI v2), specs/002-review-console-logic/spec.md (Logic v2)
- Контракты: specs/contracts/review-api.openapi.yaml, specs/contracts/review-api.md
- Переговоры и анализ: specs/_negotiation/CONTRACT_NEGOTIATION.md, specs/_negotiation/CONTRACT_DIFF.md, specs/_negotiation/ANALYZE.md
- План и задачи: specs/*/plan.md, specs/*/tasks.md
- Сравнение подходов: docs/sdd/COMPARISON_OPENSPEC.md
- Верификация: docs/sdd/VERIFICATION.md
- Метрики: docs/sdd/METRICS.md

Главное решение v2: плоский формат лимитов {max_lines,max_chars}; дифф обязан быть строкой.
