# Журнал экспериментов Практики 2

- Выбранный слабый артефакт Практики 1: P1-01 Result в practices/practice_01/prompts.md — zero‑shot ревью TRAINING_PR.diff.
- Что в нём нужно улучшить: структура и проверочность вывода (file:line, evidence, checks), устранение двусмысленностей и неподтверждённых утверждений, привязка к стандартам.
- Как поймём, что изменение полезно: все 6 техник дают различимые по форме артефакты, в prompts.md появятся ссылки на конкретные изменения файлов Практики 1 и воспроизводимые проверки.

| Техника | Файл эксперимента | Изменённый файл Практики 1 | Конкретное изменение | Проверка | Что отклонили |
|---|---|---|---|---|---|
| Few-shot | [few_shot/experiment.md](few_shot/experiment.md) | practices/practice_01/tests_unit.md | Добавлен юнит‑кейс на формат промпта и изоляцию diff | См. checks в Few-shot и строку 5 tests_unit.md | Аутентификацию как требование — вне diff; очередь задач — позже |
| R.C.T.F. | [rctf/experiment.md](rctf/experiment.md) | practices/practice_01/adr.md | Уточнены НФТ и маппинг 4xx/5xx в решении | См. Test Plan в RCTF | Немедленная очередь задач; обязательная аутентификация |
| Chain of Verification | [chain_of_verification/experiment.md](chain_of_verification/experiment.md) | practices/practice_01/context.md | Зафиксированы ограничения и открытые вопросы по версиям/422 | См. Verification Answers | 201 vs 200 — вынесено на согласование; аутентификация вне рамок |
| Tree of Thoughts | [tree_of_thoughts/experiment.md](tree_of_thoughts/experiment.md) | practices/practice_01/tests_integration.md | Добавлен интеграционный тест на таймаут/504 | См. раздел «Test Plan» ToT | Полная очередь задач и расширенный контракт ответа |
| RAG | [rag/experiment.md](rag/experiment.md) | practices/practice_01/tests_load.md | Уточнён сценарий лимитов размера diff и статуса 413 | См. OWASP-API4 / API-1 | Нестандартизованные статусы вместо RFC |
| ReAct | [react/experiment.md](react/experiment.md) | practices/practice_01/tests_integration.md | Добавлен тест «Prompt injection» | См. лог ReAct шага 4 | Немедленная миграция на очередь |

## Независимое ревью

| Замечание другой команды | Где исправили | Evidence |
|---|---|---|
| Двусмысленность | tree_of_thoughts/experiment.md — исправили нумерацию разделов и уточнили поведение fallback | Diff файла ToT; комментарий в fallback |
| Непроверяемое требование | rag/experiment.md — отказались от 503 без оснований RFC | Раздел «Что отклонили» в RAG |
| Пропущенный риск или источник | rctf/experiment.md — исправили evidence кавычек в R2 | Строка R2 в Risk Register |
