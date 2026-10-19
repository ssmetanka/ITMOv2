# Улучшение через Tree of Thoughts (ToT)
## 1. Сконструированный ToT-промпт
Роль: Senior Backend Engineer.

Контекст: По TRAINING_PR.diff добавлены `ReviewService.review(diff)` с прямой вставкой diff в промпт и синхронным вызовом `LLM.generate`, а также `POST /api/reviews` с невалидированным `payload: dict`. В P1-01 артефакт выявил риски: отсутствие валидации/контрактов API, prompt injection, отсутствие таймаутов/обработки ошибок, синхронность, совместимость типов.

Инструкция модели:
- Сгенерируй 3 принципиально разных архитектурных подхода к доработке сервиса ревью PR-диффов с LLM, чтобы устранить выявленные риски.
- Для каждого подхода оцени по критериям: вычислительная сложность, читаемость, поддерживаемость, риски интеграции (шкала 1–10, где 10 — лучше по данному критерию; обоснуй).
- Выбери один победивший подход или комбинируй сильные стороны, кратко обоснуй.
- Реализуй финальный артефакт: спецификация API (модели), безопасный конструктор промпта, обработка ошибок/таймаутов, схема интеграции LLM. Формат — самодостаточный инженерный документ с кодовыми фрагментами (Python/FastAPI, Pydantic), готовыми к внедрению.

Выходная структура:
- Раздел 1: Дерево альтернатив (описание 3 ветвей)
- Раздел 2: Сравнительная матрица (таблица оценок + аргументация)
- Раздел 3: Выбор пути
- Раздел 4: Финальная реализация (артефакт)

Ограничения:
- Сохранять совместимость по бизнес-функции: вход `diff: str`, выход как минимум `comment: str`.
- Минимизировать изменения интерфейсов; при необходимости — адаптеры.

## 2. Дерево мыслей и сравнительная матрица
Альтернатива A: Минимально инвазивный sync-регтайт
- Идея: Оставить sync-эндпойнт, добавить Pydantic-модели для запроса/ответа, безопасный промпт с разделителями и фиксированным форматом (JSON), try/except + ограниченный таймаут вызова LLM (через обёртку провайдера, внутренне sync), лимит размера diff. Маппинг ошибок на 422/5xx.
- Плюсы: Малый объём изменений; низкий риск интеграции; быстрый time-to-fix.
- Минусы: Потенциальная блокировка threadpool на тяжёлых запросах; ограниченная масштабируемость.

Альтернатива B: Асинхронный хендлер + неблокирующий LLM-клиент
- Идея: Перевести хендлер в async, LLM-клиент сделать async с `asyncio.wait_for` для таймаута; DI через FastAPI Depends; те же Pydantic-модели и безопасный промпт; лимиты на вход. Ошибки маппить корректно. Это баланс между качеством и сложностью.
- Плюсы: Лучшая масштабируемость под нагрузкой; контролируемые таймауты без блокировок.
- Минусы: Средняя сложность интеграции; возможно трогать оболочку LLM.

Альтернатива C: Асинхронная постановка задач (очередь)
- Идея: Декуплировать через очередь (Celery/RQ), endpoint возвращает job-id; результат получать по polling/вебхуку. В бэкграунде — таймауты, ретраи, лимиты. Строгие контракты.
- Плюсы: Наилучшая устойчивость и контроль затрат; не блокирует веб.
- Минусы: Существенная операционная и интеграционная сложность; требует инфраструктуры.

Сравнительная матрица (10 — лучше)

| Альтернатива | Вычислительная сложность | Читаемость | Поддерживаемость | Риски интеграции |
|---|---:|---:|---:|---:|
| A (sync+валид+таймаут) | 8 | 9 | 8 | 9 |
| B (async+валид+таймаут) | 9 | 8 | 8 | 8 |
| C (queue/job) | 10 | 7 | 7 | 5 |

Аргументация
- A: Простота кода и небольшие изменения повышают читаемость и снижают интеграционные риски; вычислительная эффективность ограничена threadpool.
- B: Асинхронность улучшает эффективность под I/O и масштабируемость; немного снижает читаемость за счёт async-паттернов.
- C: Вычислительно оптимально (нагрузка смещается), но высокая интеграционная цена и операционная сложность.

## 3. Выбор пути
- Победитель: B (async+валид+таймаут). Обоснование: баланс между масштабируемостью и сложностью, устраняет ключевые риски (валидация, prompt security, таймауты) без тяжёлой инфраструктуры. Из A заимствуем минимальные изменения контракта и простоту моделей; из C — идеи лимитов и ретраев как будущие улучшения.

## 4. Реализованный финальный артефакт
API модели (Pydantic)
```python
from pydantic import BaseModel, Field, constr

class ReviewRequest(BaseModel):
    diff: constr(min_length=1, strip_whitespace=False) = Field(..., description="Unified diff text")

class ReviewResponse(BaseModel):
    comment: str
```

Безопасный конструктор промпта
```python
PROMPT_SYSTEM = (
    "You are an AI code reviewer. Analyze the provided unified diff strictly within the diff section. "
    "Identify up to 3 high-severity risks (reliability, security, performance, API contracts). "
    "Respond ONLY in JSON matching the schema: {\"summary\": str, \"risks\": [ {\"file_line\": str, \"evidence\": str, \"rule\": str, \"check\": str } ] }."
)

def build_prompt(diff: str) -> str:
    # Isolate user input and constrain output format
    return (
        f"<system>\n{PROMPT_SYSTEM}\n</system>\n"
        f"<diff>\n{diff}\n</diff>\n"
        "<instructions>Return valid JSON only. Do not include markdown fences.</instructions>"
    )
```

LLM протокол и обёртка (async + таймаут)
```python
from typing import Protocol
import asyncio

class LLM(Protocol):
    async def generate(self, prompt: str) -> str: ...

class LLMClient:
    def __init__(self, provider: LLM, timeout_s: float = 15.0) -> None:
        self._provider = provider
        self._timeout_s = timeout_s

    async def safe_generate(self, prompt: str) -> str:
        try:
            return await asyncio.wait_for(self._provider.generate(prompt), timeout=self._timeout_s)
        except asyncio.TimeoutError as e:
            raise RuntimeError("llm_timeout") from e
        except Exception as e:  # narrow in real impl
            raise RuntimeError("llm_error") from e
```

Сервис ревью
```python
import json
from typing import Any, Dict

class ReviewService:
    def __init__(self, llm_client: LLMClient, max_diff_len: int = 100_000) -> None:
        self.llm = llm_client
        self.max_diff_len = max_diff_len

    async def review(self, diff: str) -> Dict[str, str]:
        if len(diff) > self.max_diff_len:
            # truncate conservatively; alternatively, reject with 413 in API layer
            diff = diff[: self.max_diff_len]
        prompt = build_prompt(diff)
        raw = await self.llm.safe_generate(prompt)
        # Parse and validate minimal contract; in production validate against JSONSchema
        try:
            data: Any = json.loads(raw)
            summary = data.get("summary")
            if not isinstance(summary, str):
                raise ValueError("invalid summary")
            # Keep outward contract minimal for DX
            return {"comment": summary}
        except Exception:
            # Fallback: возвращаем raw как comment, чтобы не провалить запрос полностью
            # Примечание: в проде следует логировать факт парсинговой ошибки без утечки содержимого ответа (см. OBS-1)
            return {"comment": raw if isinstance(raw, str) else "Review generation failed"}
```

FastAPI endpoint (async, DI, коды ошибок)
```python
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI()

def get_service() -> ReviewService:
    # Wire real LLM provider here
    provider: LLM = ...  # type: ignore
    client = LLMClient(provider, timeout_s=15.0)
    return ReviewService(client)

@app.post("/api/reviews", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
async def create_review(payload: ReviewRequest, svc: ReviewService = Depends(get_service)) -> ReviewResponse:
    try:
        result = await svc.review(payload.diff)
        return ReviewResponse(**result)
    except RuntimeError as e:
        message = str(e)
        if message == "llm_timeout":
            raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="LLM timeout")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="LLM provider error")
```

Примечания к интеграции
- Совместимость: внешний контракт сохраняет поле `comment: str`. Внутренний формат ответа LLM нормализуется в summary.
- Расширяемость: можно добавить rate limiting и аутентификацию на уровне FastAPI middleware; лимит размера diff — 413.
- Тесты: интеграционные для 200/422/502/504; юнит-тесты на build_prompt, парсинг JSON, таймауты.

Карта рисков, закрытых финальной реализацией
- Валидация и чёткий контракт API: `ReviewRequest`/`ReviewResponse` + `response_model`.
- Prompt injection и нестабильный формат: секционирование `<system>/<diff>`, явный JSON-контракт и парсинг.
- Таймауты/ошибки: `asyncio.wait_for`, маппинг `504/502`.
- Синхронность: async endpoint и LLM-клиент снижают блокировки.

## Что отклонили
- Полная очередь задач (Celery/RQ) — избыточно для учебного сценария и текущего объёма; зафиксировано как возможная эволюция.
- Расширение внешнего контракта на сложную схему с множеством полей — сохранён минимальный контракт `comment: str` для совместимости.

Автор: Караханов Максим
