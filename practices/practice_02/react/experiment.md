# Улучшение через паттерн ReAct

- Цель: пошагово собрать проверяемый артефакт ревью TRAINING_PR.diff, чередуя размышления и действия (тесты/проверки), чтобы подтвердить ключевые риски и сформировать итоговый ответ.
- Доступные входы: TRAINING_PR.diff; правила из CASE.md и context.md Практики 1.
- Разрешённые действия: симулированные вызовы инструментов — `run_integration_test(name)`, `run_unit_test(name)`, `search_diff(regex)`, `check_http_mapping(scenario)`.
- Запрещённые действия: изменять код; одобрять/отклонять PR; делать выводы без evidence.
- Максимальное число шагов: 5.
- Условие остановки и вопроса человеку: если не удаётся найти evidence в diff или результаты тестов противоречивы — остановиться и спросить владельца PR о намерениях контракта ответа.

## 1. Сконструированный ReAct‑промпт
Инструкция для модели:
- Формат цикла: Thought [i] → Action [i] → Observation [i]. Минимум 3 итерации.
- Доступные действия: search_diff, run_integration_test, run_unit_test, check_http_mapping.
- Требуется: по итогам собрать Final Answer с Summary и до 3 рисков (file:line, evidence, rule, check).

## 2. Лог выполнения ReAct‑цикла

| Шаг | Действие | Наблюдение | Решение продолжить или остановиться |
|---|---|---|---|
| 1 | Thought: Проверю, есть ли валидация запроса у POST `/api/reviews`. Action: search_diff(`create_review\(payload: dict\)`) | Observation: найдено `def create_review(payload: dict) -> dict[str, str]` и `return review_service.review(payload["diff"])` в app/api.py:+35..+38 | Продолжаю: подтвердить отсутствие 422 через интеграционный тест |
| 2 | Thought: Воспроизведу некорректные тела запроса. Action: run_integration_test(`missing_diff_422`) | Observation: ожидание — 422; фактический результат (по текущему коду) — `KeyError` и 500 | Зафиксировать риск №1; продолжить к промпту LLM |
| 3 | Thought: Проверю безопасность промпта. Action: search_diff(`Review this pull request and find problems:`) | Observation: найдено `prompt = f"Review this pull request and find problems:\n{diff}"` в app/review_service.py:+20 — прямое включение diff | Продолжаю: смоделировать инъекцию и отсутствие формата ответа |
| 4 | Thought: Смоделирую вредную инструкцию в diff. Action: run_unit_test(`prompt_injection_delimiters`) | Observation: тест провален — в текущем варианте нет разделителей/схемы ответа | Зафиксировать риск №2; перейти к таймаутам/ошибкам провайдера |
| 5 | Thought: Проверю маппинг таймаутов/ошибок LLM. Action: check_http_mapping(`llm_timeout_then_504`) | Observation: обработка отсутствует; синхронный вызов без try/except и таймаута | Зафиксировать риск №3; остановиться, собрать финальный ответ |

## 3. Финальный артефакт (Final Answer)
Summary
- Эндпойнт `POST /api/reviews` принимает «сырой» `dict` и обращается к `payload["diff"]` без валидации; сервис формирует промпт путём прямой вставки diff и синхронно вызывает `LLM.generate` без таймаута/обработки ошибок.

Риски (подтверждены по diff и проверкам)
1) file:line: app/api.py:+37 — evidence: `return review_service.review(payload["diff"])`. rule: Валидация входа/DX. check: интеграционный тест `missing_diff_422` демонстрирует 500 вместо 422.
2) file:line: app/review_service.py:+20 — evidence: `prompt = f"Review this pull request and find problems:\n{diff}"`. rule: Безопасность промптов/формат ответа. check: юнит‑тест `prompt_injection_delimiters` падает, т.к. нет изоляции и схемы.
3) file:line: app/review_service.py:+21 — evidence: `answer = self.llm.generate(prompt)`. rule: SLA/таймауты/обработка ошибок. check: проверка `llm_timeout_then_504` показывает отсутствие маппинга таймаута на 504.

## 4. Что изменили в исходном артефакте
- Файл и раздел: practices/practice_01/tests_integration.md — добавлен тест «Prompt injection» для проверки изоляции ввода и формата ответа.
- Изменение: новая строка теста с шагами воспроизведения вредной инструкции и ожиданием стабильного формата.
- Как проверили: прогнали логические сценарии в рамках ReAct и сверили с diff; тестовые описания согласованы с рисками.
- Что отклонили: немедленную миграцию на асинхронную очередь — не требуется для подтверждения рисков; оставлено на будущее.

Автор: Караханов Максим
