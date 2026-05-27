from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Применяет миграции и заполняет магазин демо-данными в полном объеме."

    def handle(self, *args, **options):
        self.stdout.write("Применение миграций базы данных...")
        call_command("migrate", interactive=False)
        self.stdout.write("Запуск заполнения базы данных...")
        call_command("seed_store")
        self.stdout.write(self.style.SUCCESS("База данных успешно создана и заполнена!"))
