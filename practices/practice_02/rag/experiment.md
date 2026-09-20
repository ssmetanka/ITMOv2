# Улучшение через RAG-ориентированный промптинг
## 1. Сконструированный RAG-промпт
<context>
- FastAPI Docs — Request Body & Response Model [FastAPI-ReqBody, FastAPI-RespModel]
  - "You can declare a request body using Pydantic models... FastAPI will validate the data and generate OpenAPI docs." [FastAPI-ReqBody]
  - "Use response_model to declare the response model... FastAPI will filter and document the output." [FastAPI-RespModel]
- HTTP Semantics — RFC 9110
  - "422 Unprocessable Content: the server understands the content type... but was unable to process the contained instructions." [RFC9110-422]
  - "502 Bad Gateway: the server, while acting as a gateway... received an invalid response from an inbound server." [RFC9110-502]
  - "504 Gateway Timeout: the server, while acting as a gateway... did not receive a timely response from an upstream server." [RFC9110-504]
- PEP 585 — Type Hinting Generics In Standard Collections [PEP-585]
  - "PEP 585 introduces type hinting generics for built-in collections (e.g., dict[str, int]) in Python 3.9 and later." [PEP-585]
- OWASP Top 10 for LLM — LLM01: Prompt Injection [OWASP-LLM01]
  - "Isolate untrusted input (e.g., delimiters) and constrain outputs to a strict schema to mitigate prompt injection." [OWASP-LLM01]
- OWASP API Security Top 10 — API4:2019 Lack of Resources & Rate Limiting [OWASP-API4]
  - "Implement rate limiting and input size restrictions to protect against resource exhaustion and cost amplification." [OWASP-API4]

References:
- [FastAPI-ReqBody] https://fastapi.tiangolo.com/tutorial/body/
- [FastAPI-RespModel] https://fastapi.tiangolo.com/tutorial/response-model/
- [RFC9110-422] RFC 9110, Section 15.5.20
- [RFC9110-502] RFC 9110, Section 15.6.3
- [RFC9110-504] RFC 9110, Section 15.6.5
- [PEP-585] https://peps.python.org/pep-0585/
- [OWASP-LLM01] https://owasp.org/www-project-top-10-for-large-language-model-applications/
- [OWASP-API4] https://owasp.org/API-Security/editions/2019/en/0xa4-risky-apis/
</context>

Инструкции
- Использовать только факты из <context> и предоставленного diff (TRAINING_PR.diff). Не придумывать неподтверждённое поведение.
- Для каждого вывода указывать ссылки на соответствующие метки из <context>.
- Приоритизировать вопросы надёжности, безопасности и контрактов API. Ошибки клиента маппить на 4xx (422 по [RFC9110-422]), сбои апстрима (LLM) — на 5xx (502/504 по [RFC9110-502], [RFC9110-504]).
- Обеспечить валидацию тела запроса через Pydantic и указание модели ответа [FastAPI-ReqBody], [FastAPI-RespModel].
- Снижать риск prompt injection за счёт изоляции недоверенного ввода и жёсткого формата вывода [OWASP-LLM01].
- Учитывать ограничения типизации Python по [PEP-585] и меры против истощения ресурсов [OWASP-API4].

Задача
- Проанализировать TRAINING_PR.diff и подготовить «заземлённый» артефакт: Summary и до 3 рисков с Evidence (из diff), Rule/Standard reference (из <context>), Repro check и Mitigation, согласованные с цитируемыми источниками.

## 2. Новый заземлённый артефакт
Summary
- TRAINING_PR.diff добавляет `ReviewService.review(diff)`, который строит промпт с прямой вставкой diff и синхронно вызывает `LLM.generate`, возвращая `{"comment": answer}`. Также добавлен эндпойнт `POST /api/reviews`, принимающий `payload: dict` и напрямую обращающийся к `payload["diff"]`. Отсутствие валидации запроса и модели ответа противоречит рекомендациям FastAPI [FastAPI-ReqBody, FastAPI-RespModel], что ведёт к пробелам в обработке 422 [RFC9110-422]; промпт уязвим к prompt injection [OWASP-LLM01]; отсутствует маппинг таймаутов/ошибок апстрима на 5xx [RFC9110-502], [RFC9110-504]. Типизация `dict[str, str]` требует Python 3.9+ [PEP-585].

Риски (до 3)
1) Нет валидации запроса и модели ответа (FastAPI)
   - Evidence: app/api.py:+37 `return review_service.review(payload["diff"])` при сигнатуре `def create_review(payload: dict) -> dict[str, str]`.
   - Rule/Standard: Требования FastAPI к телу запроса и модели ответа [FastAPI-ReqBody, FastAPI-RespModel]; ошибки валидации клиента должны возвращать 422 [RFC9110-422].
   - Repro check: POST `/api/reviews` с `{}` или `{ "diff": 123 }` → ожидается 422 по [RFC9110-422]; текущая реализация вероятно бросит `KeyError/TypeError` и вернёт 500.
   - Mitigation: Определить Pydantic‑модель `ReviewRequest` с `diff: str` и указать `response_model` для эндпойнта согласно [FastAPI-ReqBody], [FastAPI-RespModel], обеспечив 422 на невалидных телах [RFC9110-422].

2) Риск prompt injection и отсутствие жёсткого формата вывода
   - Evidence: app/review_service.py:+20 `prompt = f"Review this pull request and find problems:\n{diff}"` — diff включён без изоляции и без схемы ответа.
   - Rule/Standard: Изолировать недоверенный ввод и ограничить формат вывода [OWASP-LLM01].
   - Repro check: Передать diff с вредной инструкцией (например, "IGNORE PREVIOUS INSTRUCTIONS") → модель может последовать ей.
   - Mitigation: Обрамлять diff разделителями (например, `<diff>...</diff>`) и задавать строгую JSON‑схему ответа, валидируя результат [OWASP-LLM01].

3) Нет таймаутов/обработки ошибок апстрима LLM
   - Evidence: app/review_service.py:+21 `answer = self.llm.generate(prompt)` — без timeout/try‑except, синхронный вызов.
   - Rule/Standard: Маппить ошибки/таймауты апстрима на 5xx [RFC9110-502], [RFC9110-504].
   - Repro check: Замокать `generate`, чтобы он зависал или бросал исключение → текущая реализация вероятно повиснет или вернёт 500.
   - Mitigation: Ввести таймаут вокруг вызова LLM; при таймауте возвращать 504 [RFC9110-504], при ошибке апстрима — 502 [RFC9110-502].

Дополнительные заметки
- Тип `dict[str, str]` опирается на дженерики из PEP 585 (Python 3.9+) [PEP-585]. Если целимся ниже — избегать этого синтаксиса.
- Рассмотреть лимиты по размеру diff и rate limiting для защиты от истощения ресурсов [OWASP-API4].

## 3. Оценка надёжности
- Привязка к руководствам FastAPI по моделям запроса/ответа обеспечивает обоснованность рекомендаций про 422 и схемы, избегая общих советов из слабого P1‑01.
- Ссылки на RFC 9110 для кодов 422/502/504 предотвращают неправильное использование семантики HTTP и выравнивают маппинг ошибок со стандартами.
- OWASP LLM01 даёт конкретные меры (изоляция ввода, строгие схемы вывода) против prompt injection вместо разрозненных идей из слабого ответа.
- Упоминание PEP 585 проясняет ограничения версии Python для `dict[str, str]`, исключая скрытые предположения о совместимости.
- OWASP API4 подчёркивает контроль ресурсов (лимиты размера, rate limiting), что ранее лишь подразумевалось.
 - OWASP API4 подчёркивает контроль ресурсов (лимиты размера, rate limiting), что ранее лишь подразумевалось.

## Что отклонили
- Идею маппить любую ошибку LLM в 503 Service Unavailable — по RFC для прокси‑сценариев уместнее 502/504 [RFC9110-502], [RFC9110-504].
- Предложение использовать произвольные самодельные статусы — противоречит RFC; оставили только стандартизованные коды.

Автор: Караханов Максим
