from django.core.management.base import BaseCommand
import pyodbc
from config.settings import SQL_LOGIN, SQL_PASS, SQL_SERVER, SQL_DRIVER, SQL_DB,SQL_DB_FIRST_CONNECTDB

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Формирование строки подключения
        ConnectionString = f'''
            DRIVER={{{SQL_DRIVER}}};
            SERVER={SQL_SERVER};
            DATABASE={SQL_DB};
            UID={SQL_LOGIN};
            PWD={SQL_PASS}
        '''

        try:
            # Подключение к БД
            conn = pyodbc.connect(ConnectionString)
            conn.autocommit = True  # Автофикс изменений
            
            # Создание базы данных
            conn.execute(f'CREATE DATABASE {SQL_DB};')
            
        except pyodbc.ProgrammingError as ex:
            # Вывод ошибки при создании БД
            print(ex)
        else:
            # Вывод сообщения об успешном создании
            print(f'База данных {SQL_DB} успешно создана')