# AI-Review Constitution

## Core Principles

### I. Contract-First
- Единственный контракт требований — docs/requirements.md. Изменения контракта запрещены. API/UI обязаны следовать контракту и согласованным спецификациям.

### II. Minimal Dependencies
- Только стандартная библиотека Python/Node. Для UI — ванильный HTML/JS без фреймворков и npm-зависимостей.

### III. Test-Driven Development (NON-NEGOTIABLE)
- Сначала падающий тест, затем реализация, затем зелёный прогон. scripts/check.sh — единственный раннер.

### IV. Types and Clarity
- Аннотации типов где применимо, понятные имена, короткие функции. Минимальные, точечные изменения.

### V. Separation of Concerns
- UI и сервер взаимодействуют через общий контракт и фикстуры. Лимиты — источник истины сервер.

## Additional Constraints
- Не использовать git команды. Все артефакты хранятся в practice_05/.
- Исторический проект practice_04/ — read-only.

## Development Workflow
- Шаги A–I из practice_05/prompt.md соблюдаются, контрольные точки фиксируются в docs/sdd/CHECKPOINTS.md.
- Сквозные проверки через контрактные фикстуры.

## Governance
- Конституция обязательна к соблюдению. Изменения конституции фиксируются с обоснованием в DECISIONS.md.

Version: 1.0 | Ratified: auto | Last Amended: auto
