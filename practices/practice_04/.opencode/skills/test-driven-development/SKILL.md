---
name: test-driven-development
description: Применение дисциплины TDD (Red-Green-Refactor) для надежной реализации фич
---

# Test Driven Development Procedure

1. **Red**: Напиши минимальный изолированный тест, воспроизводящий требование. Запусти `sh scripts/check.sh` и убедись, что тест падает с ожидаемой ошибкой.
2. **Green**: Напиши минимально необходимый код реализации, пока `sh scripts/check.sh` не станет успешен.
3. **Refactor**: Очисти код от дублирования, не ломая зелёные тесты.

