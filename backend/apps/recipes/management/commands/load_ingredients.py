"""Management команда для загрузки ингредиентов из CSV файла."""
import csv
import os

from apps.recipes.models import Ingredient
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Команда для загрузки ингредиентов из CSV файла."""

    help = "Загружает ингредиенты из CSV файла в базу данных"

    def add_arguments(self, parser):
        """Добавляет аргументы командной строки."""
        parser.add_argument(
            "--file",
            type=str,
            help="Путь к CSV файлу с ингредиентами",
            default="data/ingredients.csv",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить таблицу ингредиентов перед загрузкой",
        )

    def handle(self, *args, **options):
        """Основная логика команды."""
        file_path = options["file"]

        # Определяем путь к файлу
        if not os.path.isabs(file_path):
            # Пробуем разные варианты пути
            possible_paths = [
                # Для Docker контейнера (файл монтируется в /app/data/)
                os.path.join("/app", file_path),
                # Для локальной разработки (от корня проекта)
                os.path.join(settings.BASE_DIR.parent, file_path),
                # Альтернативный путь для Docker
                os.path.join("/data", "ingredients.csv"),
                # Прямой путь от BASE_DIR
                os.path.join(settings.BASE_DIR, file_path),
            ]

            # Ищем существующий файл
            for path in possible_paths:
                if os.path.exists(path):
                    file_path = path
                    break
            else:
                # Если файл не найден, выводим информацию для отладки
                self.stdout.write(
                    self.style.ERROR("Файл не найден. Проверенные пути:")
                )
                for path in possible_paths:
                    self.stdout.write(f"  - {path}")

                # Показываем текущую директорию и её содержимое
                current_dir = os.getcwd()
                self.stdout.write(f"Текущая директория: {current_dir}")

                raise CommandError(f"Файл не найден: {options['file']}")

        if not os.path.exists(file_path):
            raise CommandError(f"Файл не найден: {file_path}")

        # Очищаем таблицу если нужно
        if options["clear"]:
            self.stdout.write(
                self.style.WARNING("Очищаю таблицу ингредиентов...")
            )
            Ingredient.objects.all().delete()

        # Загружаем ингредиенты
        self.stdout.write(f"Загружаю ингредиенты из {file_path}...")

        created_count = 0
        skipped_count = 0

        with open(file_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)

            for row_num, row in enumerate(reader, 1):
                if len(row) != 2:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Строка {row_num}: неверное количество "
                            f"полей: {row}"
                        )
                    )
                    continue

                name, measurement_unit = row
                name = name.strip()
                measurement_unit = measurement_unit.strip()

                if not name or not measurement_unit:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Строка {row_num}: пустые поля: {row}"
                        )
                    )
                    continue

                # Создаем или получаем ингредиент
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit,
                )

                if created:
                    created_count += 1
                    if created_count % 100 == 0:
                        self.stdout.write(
                            f"Создано {created_count} ингредиентов..."
                        )
                else:
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Загрузка завершена! "
                f"Создано: {created_count}, "
                f"Пропущено: {skipped_count}"
            )
        )
