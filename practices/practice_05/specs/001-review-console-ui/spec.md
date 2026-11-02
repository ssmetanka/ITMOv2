# Review Console UI — v2

## User Stories (prioritized)
- US-1: Как пользователь, я хочу вставить diff и увидеть счётчик строк/символов с подсветкой превышения, чтобы понять, можно ли отправлять.
- US-2: Как пользователь, я хочу кнопкой «Проверить» или Ctrl+Enter отправить diff и получить результат ревью.
- US-3: Как пользователь, я хочу видеть панель «Последние ревью» с 5 последними, клик по записи открывает сохранённый результат.

## Functional Requirements
- FR-UI-001: Поле ввода diff с живым счётчиком (строки/символы), лимиты подсвечиваются при превышении.
- FR-UI-002: Кнопка «Проверить» неактивна при пустом или слишком большом вводе; Ctrl+Enter = отправка; при loading кнопка блокируется.
- FR-UI-003: Состояния экрана (FSM): idle, loading, success, validation_error, llm_unavailable, network_error; пустая история отображается корректно.
- FR-UI-004: Панель истории: показывает последние 5; клик по записи отображает сохранённое ревью.
- FR-UI-005: aria-live для статусов.

## Given/When/Then Scenarios
- S-1: Given пустой ввод When ввод фокуса Then кнопка disabled, подсказка.
- S-2: Given валидный diff When Ctrl+Enter Then отправка, состояние loading, затем success.
- S-3: Given превышение лимитов When ввод Then подсветка и disabled.
- S-4: Given llm_unavailable от API When повтор Then повтор запроса.
- S-5: Given пустая история When загрузка Then отдельный пустой стейт.

## Edge Cases
- E-1: Ровно на лимите — отправка возможна.
- E-2: Плохая сеть → network_error.

## Success Criteria
- Все состояния отображаются и соответствуют контракту.

## Out of Scope
- Нет аутентификации, нет сторонних зависимостей, без SPA-фреймворков.

## Допущения об интерфейсе с другой командой
- UI ожидает API: GET /api/limits; POST /api/reviews; GET /api/reviews?limit=5; GET /api/reviews/{id}.
- Формат ошибок: error.code, error.message, error.details; коды DIFF_EMPTY, DIFF_TOO_LARGE, LLM_UNAVAILABLE, INVALID_REQUEST, NOT_FOUND.
- Формат лимитов — плоский {max_lines,max_chars}.
