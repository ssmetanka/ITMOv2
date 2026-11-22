| ID | Первоначальное описание | Тест | Исправление | Статус |
|---|---|---|---|---|
| F-01/F01 | IDOR/SQLi в профиле | lab/test_security.py::test_fix_F01_profile_idor_and_injection | Параметризованные запросы и скоуп по сессии (ранее реализовано) | Fixed |
| F-04/F04 | Листинг заказов вне скоупа | lab/test_security.py::test_fix_F04_orders_listing_scoped | Селект по owner (ранее реализовано) | Fixed |
| F-05/F05 | Подмена цены заказа | lab/test_security.py::test_fix_F05_catalog_price_enforced | Цена берется из каталога (ранее реализовано) | Fixed |
| F-06/F06 | Экспорт без staff-сессии | lab/test_security.py::test_fix_F06_admin_export_requires_staff_session | Проверка роли по серверной сессии | Fixed |
| F-07/F07 | Чтение чужих файлов | lab/test_security.py::test_fix_F07_files_enforce_user_scope | Привязка к username из сессии | Fixed |
| F-09/F09 | Инструменты помощника выходят за права | lab/test_security.py::test_fix_F09_assistant_execute_scoped_tools | Схема и скоуп инструментов | Fixed |
| F-12/F12 | Доступ к логам | lab/test_security.py::test_fix_F12_logs_protected | Требуется staff | Fixed |
| F-08 | Не зафиксирован отдельным тестом | — | Н/Д | Unknown/Test missing |
| N-01 | SQLi и IDOR в /assistant/context | lab/test_security.py::test_assistant_context_requires_auth_and_owner_scope | Авторизация, параметризация, скрытие существования чужих заказов | Fixed |
| N-02 | Stored XSS в отзывах | lab/test_http.py::test_reviews_are_escaped_over_http; lab/test_security.py::test_reviews_xss_escaped_and_auth_required | Экранирование html.escape и авторизация | Fixed |
| N-03 | Утечка секретов в логах | lab/test_security.py::test_logs_do_not_leak_passwords_or_tokens | Маскирование чувствительных полей/заголовков и query | Fixed |
| N-04 | Опасный delete_tree | lab/test_security.py::test_delete_tree_disabled | Инструмент отключен | Fixed |
| N-05 | Раскрытие внутренних ошибок | Нужны офлайн проверки | Унификация 500 с request_id | Fixed |
