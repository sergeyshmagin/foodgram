#!/usr/bin/env python3
"""
Скрипт для проверки и автоматического исправления кода в соответствии с PEP8
"""
import subprocess
import sys


def run_command(cmd, description):
    """Запуск команды с выводом результата."""
    print(f"\n🔍 {description}")
    print("=" * 50)

    try:
        result = subprocess.run(
            cmd.split(), capture_output=True, text=True, check=False
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode != 0:
            print(f"❌ Ошибки найдены (код возврата: {result.returncode})")
            return False
        else:
            print("✅ Проверка пройдена")
            return True

    except FileNotFoundError:
        print(f"❌ Команда не найдена: {cmd.split()[0]}")
        return False


def main():
    """Основная функция проверки кода."""
    print("🚀 Запуск проверки кода...")

    # Директории для проверки
    paths = ["apps/", "foodgram/", "tests/"]
    paths_str = " ".join(paths)

    # Список проверок
    checks = [
        (f"python -m flake8 {paths_str}", "Проверка flake8 (PEP8)"),
        (
            f"python -m black --check --diff {paths_str}",
            "Проверка форматирования black",
        ),
        (
            f"python -m isort --check-only --diff {paths_str}",
            "Проверка сортировки импортов",
        ),
        ("python -m bandit -r apps/ -f json", "Проверка безопасности bandit"),
    ]

    all_passed = True

    for cmd, description in checks:
        if not run_command(cmd, description):
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Все проверки пройдены успешно!")
    else:
        print("❌ Некоторые проверки провалились. Исправьте ошибки.")
        print("\n💡 Для автоматического исправления запустите:")
        print("   python lint.py --fix")

    return 0 if all_passed else 1


def fix_code():
    """Автоматическое исправление кода."""
    print("🔧 Автоматическое исправление кода...")

    paths = ["apps/", "foodgram/", "tests/"]
    paths_str = " ".join(paths)

    fixes = [
        (f"python -m black {paths_str}", "Форматирование с black"),
        (f"python -m isort {paths_str}", "Сортировка импортов с isort"),
    ]

    for cmd, description in fixes:
        run_command(cmd, description)

    print("\n🎯 Повторная проверка после исправлений:")
    return main()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        sys.exit(fix_code())
    else:
        sys.exit(main())
