# DECISIONS

Дата: $(date -Is)

1. Framework choice: GitHub Spec Kit (specify)
   Причина: открыт, интегрируется с opencode, поддерживает цепочку constitution → specify → clarify → plan → tasks → analyze → implement и каталог contracts/.

2. Установка Spec Kit: использован `uv tool install specify-cli` с репозиторием git+https://github.com/github/spec-kit.git. Команда `specify init . --force` выполнена успешно. Флаг `--ai` недоступен в этой версии — задокументировано.

3. Безопасность исходного проекта: до изменений создана резервная копия `cp -a . /tmp/ai-review-baseline` (см. инструкции), baseline-вывод `scripts/check.sh` сохранён в `docs/sdd/baseline.txt`.

4. Режим работы: соблюдаем brownfield-подход — существующий код и тесты не изменяются. Все новые артефакты в practice_05/.

5. Эмуляция субагентов: субагенты опциональны. В этом выполнении спецификации двух команд будут эмулированы последовательной работой (team-ui затем team-logic) с фиксацией контрольных точек и честной пометкой в CHECKPOINTS/DECISIONS.

6. SPECIFY_FEATURE переменные: используем имена 001-review-console-ui и 002-review-console-logic для структурирования в specs/.
