#!/usr/bin/env python3
"""
Быстрая проверка кода перед деплоем
"""
import subprocess
import sys


def run_check():
    """Запуск проверки flake8."""
    print("🔍 Проверка кода перед деплоем...")

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "flake8",
                "backend/apps/",
                "backend/foodgram/",
                "--exclude=migrations,venv,.venv",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Код чист! Готов к деплою.")
            return True
        else:
            print("❌ Найдены ошибки:")
            print(result.stdout)
            return False

    except FileNotFoundError:
        print("❌ flake8 не найден. Установите: pip install flake8")
        return False


if __name__ == "__main__":
    success = run_check()
    sys.exit(0 if success else 1)
