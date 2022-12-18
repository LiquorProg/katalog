from PyQt5.QtSql import *
import sys

db_name = 'data_bases/data.db'


"""Подключение к базе данных"""
def connect_db(db_name):
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_name)
    if not db.open():
        print('No connection database')
        return False
    return db

"""Проверка подключения к базе данных"""
if not connect_db(db_name):
    sys.exit(-1)
else:
    print('Connection OK')

