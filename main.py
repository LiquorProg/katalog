from PyQt5 import QtSql
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui, QtWidgets

from MainForm import Ui_MainWindow
from case_record import Ui_Dialog
import sqlite3
import sys


def otherWindow(): #Карточка пациента
    global Dialog
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()

    """Автонумирование для новой карточки пациента"""
    cursor.execute("select max(patients_id) from patients")
    result = cursor.fetchall()
    ui.card_number.setText(f'№{result[0][0]+1}')

    """Внесение всей информации из ячеек в базу данных и закрытие окна"""
    def savePat():
        print(info := ui.general_chatacteristics.toPlainText())
        print(street := ui.street_name.text())
        print(affil := ui.affiliation.text())
        print(mobile := ui.mobile_1.text())
        print(house_numb := ui.house_number.text())
        cursor.execute(f"""INSERT INTO patients(full_name, age, info, street, affiliation, mobile_1, house_numb) VALUES('dasha', 34, '{info}', '{street}', '{affil}', '{mobile}', {house_numb})""")
        db.commit()
        Dialog.close()

    ui.saveButton.clicked.connect(savePat)#Кнопка сохранения информациия занесённой в ячейках в базу данных

def katalog(): #Главная страница со списком карточек
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    ui.pushButton.clicked.connect(otherWindow) #Подключение к кнопке открытие нового окна

    """Создание екземляра класса QSqlTableModel, установка таблицы patients"""
    Patients = QSqlTableModel()
    Patients.setTable('patients')
    Patients.select()

    """Связывание таблици базы данных с обьектом 'tableView' и сортирока по столбцам"""
    ui.tableView.setModel(Patients)
    ui.tableView.setSortingEnabled(True)

    sys.exit(app.exec())

if __name__ == '__main__':
    with sqlite3.connect('data_bases/data.db') as db:
        cursor = db.cursor()
        katalog()
