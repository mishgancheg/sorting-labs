"""Хук автоматической проверки: запуск pytest после редактирования файлов проекта.

Скрипт вызывается харнессом Claude Code (событие PostToolUse) после каждого
редактирования или создания файла. Из входного потока (JSON) берётся путь
изменённого файла; если это Python-файл внутри проекта, запускаются тесты
pytest. Результат возвращается агенту: при падении тестов код выхода 2,
и сообщение об ошибке попадает прямо в диалог.

Файл лежит в .claude/hooks/ и является частью харнесса проекта, а не
временным скриптом.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Корень проекта — два уровня вверх от этого файла (.claude/hooks/).
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# Python из виртуального окружения проекта.
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"


def main() -> int:
    payload = json.load(sys.stdin)
    # Поле tool_input.file_path содержит путь изменённого файла.
    file_path = Path(payload.get("tool_input", {}).get("file_path", ""))
    if file_path.suffix != ".py":
        # Изменён не Python-файл (документ, настройки) — тесты не нужны.
        return 0

    result = subprocess.run(
        [str(VENV_PYTHON), "-m", "pytest", "tests/", "-q", "--no-header"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode == 0:
        # Всё хорошо: краткая сводка в stderr идёт агенту как уведомление.
        print(result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "тесты пройдены", file=sys.stderr)
        return 0

    # Тесты упали: печатаем краткий отчёт и сообщаем агенту кодом выхода 2.
    print("pytest обнаружил ошибки после изменения файла:", file=sys.stderr)
    print(result.stdout, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
