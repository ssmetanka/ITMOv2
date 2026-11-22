# Plan (UI) — v2
1. UI-001 INIT-UI: загрузка лимитов /api/limits — files: ui/app.js — done: counter отражает лимиты.
2. UI-002 INPUT-METRICS: счётчики строк/символов — files: ui/state.js — done: tests pass.
3. UI-003 FSM: idle/loading/success/validation_error/llm_unavailable/network_error — files: ui/state.js, ui/app.js — done: статусы отображаются.
4. UI-004 HISTORY: загрузка и отображение 5 последних — files: ui/app.js — done: список при старте.
5. UI-005 SUBMIT LOCK: блок повторной отправки — files: ui/app.js — done: кнопка disabled при loading.
