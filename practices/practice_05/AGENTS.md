# Правила работы агента в проекте AI-Review

- Контракт требований: docs/requirements.md
- Пример тестов: tests/test_review.py
- Команда автоматической проверки: sh scripts/check.sh
- Руководство по стилю: docs/style-guide.md

Среда OpenCode: агенты используют конфигурацию opencode.json. MCP сервер diff-guard предоставляет tool validate_diff_stats. Хуки: проверка запускается scripts/check.sh после правок через плагин @opencode-ai/plugin при наличии конфигурации .opencode.

## Ограничения
1. Не меняй контракт (docs/requirements.md) и тест-раннер без прямого указания.
2. Сначала запускай проверку, подтверждай падение нового теста (TDD), затем пиши реализацию.
3. Перед редактированием кода сверяйся с docs/style-guide.md.
