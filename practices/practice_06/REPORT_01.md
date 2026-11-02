# Отчёт 1. Атаки на исходный сервис

Резюме: фиксируются первоначальные уязвимости без утверждения об их исправлении. Подтверждение и исправления отражены в REPORT_02.md и в тестах.

Покрытие: аутентификация/авторизация — найдено; инъекции — SQL в /profile и /search; файлы — произвольное чтение; бизнес‑логика — override price; AI‑помощник — опасные инструменты без проверок; LLM‑судья — офлайн анализ; ПДн — утечки в /debug/logs; надёжность — базовый лимит тела; зависимости — stdlib.

F-01: IDOR и SQLi в /profile (lab/service.py:56-59)
Критичность: High; CWE-89, CWE-639. PoC: GET /profile?id=2 → чужой профиль; GET /profile?id=1 OR 1=1 → все.
Рекомендация: использовать сессию и параметризовать запрос.

F-02: SQLi и отсутствие ролей в /search (lab/service.py:58-60)
Критичность: High. PoC: GET /search?q=' OR '1'='1. Рекомендация: staff‑only и параметризация LIKE.

F-03: /orders раскрывает все заказы (lab/service.py:60-61)
Критичность: Medium. PoC: GET /orders → все заказы. Рекомендация: фильтр owner, staff видит всё.

F-04: Client override цены при создании заказа (lab/service.py:69)
Критичность: Medium. PoC: POST /orders {price:1}. Рекомендация: цену брать из каталога.

F-05: /admin/export доверяет X-Role (lab/service.py:75-77)
Критичность: High. PoC: без логина с X-Role: staff → данные. Рекомендация: проверять роль из сессии.

F-06: /files читает произвольные пути (lab/service.py:79-80)
Критичность: High. PoC: user=bob или path=../private/operator-note.txt. Рекомендация: только собственный чек.

F-07: /debug/logs без аутентификации (lab/service.py:81-82)
Критичность: Medium. PoC: GET /debug/logs. Рекомендация: staff‑only.

F-08: /assistant/execute выполняет опасные инструменты без проверок (lab/service.py:99-109)
Критичность: High. PoC: read_file private/operator-note.txt, export_profiles, delete_tree.
Рекомендация: allow‑list и проверки ролей/владения.
