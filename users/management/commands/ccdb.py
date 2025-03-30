from django.core.management.base import BaseCommand
import pyodbc
from config.settings import USER, PASSWORD, HOST, DRIVER, PAD_DATABASE, DATABASE


class Command(BaseCommand):
    help = 'Создает базу данных, если она не существует'

    def handle(self, *args, **options):
        # Формируем строку подключения
        ConnectionString = f'''DRIVER={DRIVER};
            SERVER={HOST};
            DATABASE={PAD_DATABASE};
            UID={USER};
            PWD={PASSWORD}'''

        try:
            # Устанавливаем соединение с сервером
            conn = pyodbc.connect(ConnectionString)
            conn.autocommit = True

            # Пытаемся создать базу данных
            conn.execute(fr'CREATE DATABASE {DATABASE};')

            # Закрываем соединение
            conn.close()

            self.stdout.write(self.style.SUCCESS(f'База данных {DATABASE} успешно создана'))
        except pyodbc.ProgrammingError as ex:
            # Обработка ошибки, например, если база данных уже существует
            self.stdout.write(self.style.ERROR(f'Ошибка при создании базы данных: {ex}'))
        except Exception as ex:
            # Обработка других ошибок
            self.stdout.write(self.style.ERROR(f'Произошла ошибка: {ex}'))
