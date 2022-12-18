from PyQt5 import QtSql
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui, QtWidgets

import data_base
from data_base import *
from MainForm import Ui_MainWindow
from case_record import Ui_Dialog

import sys


def otherWindow(): #Карточка пациента
    global Dialog
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()

    query = QSqlQuery()
    print(query.exec_("select max(patients_id) from patients"))

    new_cart_numb = query.next()
    print(new_cart_numb)
    ui.card_number.setText(f"№{new_cart_numb}")

    """Внесение всей информации из ячеек в базу данных и закрытие окна"""
    def savePat():
        print(info := ui.general_chatacteristics.toPlainText())
        print(street := ui.street_name.text())
        print(affil := ui.affiliation.text())
        print(mobile := ui.mobile_1.text())
        print(house_numb := ui.house_number.text())
        query = QSqlQuery()
        query.exec_(f"INSERT INTO patients(full_name, age, info, street, affiliation, mobile_1, house_numb) VALUES('masha', 34, '{info}', '{street}', '{affil}', '{mobile}', {house_numb})")
        Dialog.close()

    ui.saveButton.clicked.connect(savePat)

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

# def katalog():
#     Form, Window = uic.loadUiType("MainForm.ui")
#
#     app = QApplication(sys.argv)
#
#     """Главное окно"""
#     window = Window()
#
#     form = Form()
#     form.setupUi(window)
#
#     # def on_click():
#     #     case_record()
#     #
#     # form.pushButton.clicked.connect(on_click)
#
#     """Связывание таблици базы данных с обьектом 'tableView' и сортирока по столбцам"""
#     form.tableView.setModel(Patients)
#     form.columnView.setModel(Patients)
#     form.tableView.setSortingEnabled(True)
#
#     window.show()
#     sys.exit(app.exec())

if __name__ == '__main__':
    katalog() #Main_window
