| Требование | Спецификация | Реальный файл | Состояние | Что необходимо сделать |
| --- | --- | --- | --- | --- |
| GET /api/limits | logic v1/v2 | app/api.py:get_limits, server.py | Выполнено | Сохранить плоский формат |
| POST /api/reviews: diff string | logic v2 | app/api.py | Обновлено | Строгая проверка типа реализована |
| Валид. пустого diff | logic v1/v2 | reviewer.py | Выполнено | — |
| Лимит 300 строк | logic v1/v2 | reviewer.py | Выполнено | CRLF нормализован splitlines |
| Лимит 10000 символов | logic v1/v2 | reviewer.py | Обновлено | Счёт UTF-16 для согласия с JS |
| История до 50 | logic v1/v2 | history.py | Выполнено | — |
| Новые первыми | logic v1/v2 | history.py | Выполнено | — |
| 504 LLM timeout | logic v1/v2 | reviewer.py/api.py | Улучшено | Реализован мягкий таймаут через поток |
| Раздача UI | ui v2 | server.py | Добавлено | Безопасная статика /ui |
| UI счетчики и лимиты | ui v2 | ui/* | Выполнено | — |
| UI состояния | ui v2 | ui/app.js,state.js | Частично | Добавить загрузку истории/просмотр |
| Ctrl+Enter | ui v2 | ui/app.js | Выполнено | — |
| История 5 | ui v2 | ui/app.js | Частично | Загрузка при старте |
| Контракт OpenAPI | contracts | specs/contracts | Частично | Обновить markdown и diff |
| Node-тесты импорт | tests | ui/tests | Исправлено | Импорт describe/it добавлен |
| Python запускает node --test | tests | tests/test_ui_unit.py | Исправлено | Явный список файлов |
