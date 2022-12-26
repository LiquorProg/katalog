from PyQt5 import QtCore, QtGui, QtWidgets

from MainForm import Ui_MainWindow
from case_record import Ui_Dialog
from case_record_edit import Ui_Dialog_edit
import sqlite3
import sys


def otherWindow(): #Создание новой карточки пациента
    global Dialog
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()

    ui.comboBox_streets.addItems(["вулиця", "провулок", "бульвар", "шоссе", "проспект"])#Комбобокс с вариантами назв. улиц

    # def proverkaBox():
    #     print(type(ui.comboBox_streets.currentText()))
    #
    # ui.proverka.clicked.connect(proverkaBox)

    """Автонумирование для новой карточки пациента"""
    cursor.execute("select max(patients_id) from patients")
    result = cursor.fetchall()
    ui.card_number.setText(f'№{result[0][0]+1}')

    """Внесение всей информации из ячеек в базу данных и закрытие окна"""
    def savePat():
        print(name := ui.pat_name.text())
        print(info := ui.general_chatacteristics.toPlainText())
        print(street := ui.street_name.text())
        print(affil := ui.affiliation.text())
        print(mobile := ui.mobile_1.text())
        print(mobile_2 := ui.mobile_2.text())
        print(work_ph := ui.work_phone.text())
        print(home_ph := ui.home_phone.text())
        print(house_numb := ui.house_number.text())
        print(street_t := ui.comboBox_streets.currentText())
        print(manag := ui.manager.toPlainText())
        cursor.execute(f"""INSERT INTO patients(full_name, info, street, affiliation, mobile_1, mobile_2, w_phone, h_phone, house_numb, street_type, manager) 
                        VALUES('{name}', '{info}', '{street}', '{affil}', '{mobile}', '{mobile_2}', '{work_ph}', '{home_ph}', {house_numb}, '{street_t}', '{manag}')""")
        db.commit()
        Dialog.close()

    ui.saveButton.clicked.connect(savePat)#Кнопка сохранения информациия занесённой в ячейках в базу данных

def otherWindow_2(id): #Просмотр и редактирование карточки пациента
    global Dialog_edit
    Dialog_edit = QtWidgets.QDialog()
    ui = Ui_Dialog_edit()
    ui.setupUi(Dialog_edit)
    Dialog_edit.show()

    """Получение всей инф. об определенном пациенте из таблицы БД"""
    cursor.execute(f"SELECT * FROM patients WHERE patients_id = {id}")
    result = cursor.fetchall()

    def switch(status=True): #Функция для переключения статуса виджетов
        if not status:
            ui.comboBox_streets_2.clear()
            ui.comboBox_streets_2.addItems(["вулиця", "провулок", "бульвар", "шоссе", "проспект"])
            ui.comboBox_streets_2.setCurrentText(str(result[0][10]))
            ui.saveButton_2.setEnabled(True)

        ui.street_name_2.setReadOnly(status)
        ui.affiliation_2.setReadOnly(status)
        ui.mobile_1_2.setReadOnly(status)
        ui.mobile_2_2.setReadOnly(status)
        ui.work_phone_2.setReadOnly(status)
        ui.home_phone_2.setReadOnly(status)
        ui.general_chatacteristics_2.setReadOnly(status)
        ui.house_number_2.setReadOnly(status)
        ui.pat_name_2.setReadOnly(status)
        ui.manager_2.setReadOnly(status)

    def editPat(): #Занесение в БД отредактированные данные
        print(name := ui.pat_name_2.text())
        print(info := ui.general_chatacteristics_2.toPlainText())
        print(street := ui.street_name_2.text())
        print(affil := ui.affiliation_2.text())
        print(mobile := ui.mobile_1_2.text())
        print(mobile_2 := ui.mobile_2_2.text())
        print(work_ph := ui.work_phone_2.text())
        print(home_ph := ui.home_phone_2.text())
        print(house_numb := ui.house_number_2.text())
        print(street_t := ui.comboBox_streets_2.currentText())
        print(manag := ui.manager_2.toPlainText())
        cursor.execute(f"""UPDATE patients SET full_name='{name}', info='{info}', street='{street}', affiliation='{affil}', 
                        mobile_1='{mobile}', mobile_2='{mobile_2}', w_phone='{work_ph}', h_phone='{home_ph}',
                        house_numb={house_numb}, street_type='{street_t}', manager='{manag}' WHERE patients_id={id}""")
        db.commit()
        Dialog_edit.close()

    switch() #Установка виджетов в статус ReadOnly
    ui.saveButton_2.setEnabled(False) #Кнопка сохранения не активна

    """Заполнение ячеек данными полученых из БД"""
    ui.comboBox_streets_2.addItems([str(result[0][10])])
    ui.card_number_2.setText(f"№{result[0][0]}")
    ui.street_name_2.setText(str(result[0][3]))
    ui.affiliation_2.setText(str(result[0][4]))
    ui.mobile_1_2.setText(str(result[0][5]))
    ui.mobile_2_2.setText(str(result[0][6]))
    ui.work_phone_2.setText(str(result[0][7]))
    ui.home_phone_2.setText(str(result[0][8]))
    ui.general_chatacteristics_2.setText(str(result[0][2]))
    ui.house_number_2.setText(str(result[0][9]))
    ui.pat_name_2.setText(str(result[0][1]))
    ui.manager_2.setText(str(result[0][11]))

    def diagnosesTable(): #Таблица с диагнозами
        cursor.execute(f"SELECT date, apartment, full_name, diagnosis FROM patients join diagnoses using(patients_id) where patients_id = {id}")
        result = cursor.fetchall()
        print(result)
        """Заполнение таблицы"""
        ui.tableWidget_diag_edit.setRowCount(len(result))
        for row, items in enumerate(result):
            for index, item in enumerate(items):
                ui.tableWidget_diag_edit.setItem(row, index, QtWidgets.QTableWidgetItem(str(item)))

    diagnosesTable()

    ui.editButton.clicked.connect(lambda sh, stat=False: switch(stat)) #Кнопка для редактирования ячеек
    ui.saveButton_2.clicked.connect(editPat) #Кнопка сохранения

def katalog(): #Главная страница со списком карточек
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    def updateTable(sql_search=False): #таблица со списком карточек пациентов
        if not sql_search:
            """SQL запрос на инф. из 4 столбцов для добавления в виджет без фильтров"""
            cursor.execute("SELECT patients_id, street_type, street, house_numb FROM patients")
            result = cursor.fetchall()
        else:
            """SQL запрос с фильтрами"""
            cursor.execute(f"""SELECT patients_id, street_type, street, house_numb FROM patients WHERE street LIKE '%{ui.search_street.text()}%'
                                AND house_numb LIKE '{ui.search_house.text()}%' AND full_name LIKE '{ui.search_patient.text()}%' 
                                AND manager LIKE '{ui.search_manager.text()}%'""")
            print(ui.search_street.text())
            result = cursor.fetchall()

        """Заполнение таблицы"""
        ui.tableWidget.setRowCount(len(result))
        for row, items in enumerate(result):
            for index, item in enumerate(items):
                item = str(item)
                if item.isnumeric():
                    ui.tableWidget.setItem(row, index, QtWidgets.QTableWidgetItem((' '*9+str(item))[-9:]))
                else:
                    ui.tableWidget.setItem(row, index, QtWidgets.QTableWidgetItem(str(item)))

            """Создание и добавление кнопки в таблицу на открытие карточки пациента"""
            button = QtWidgets.QPushButton('Review')
            button.clicked.connect(lambda sh, id=items[0]: otherWindow_2(id))
            ui.tableWidget.setCellWidget(row, 4, button)
        ui.tableWidget.setSortingEnabled(False)
        ui.sortButton.setEnabled(True)

    def sort_table():
        ui.tableWidget.setSortingEnabled(True)  #Сортировка столбцов
        ui.sortButton.setEnabled(False)

    updateTable()

    ui.sortButton.clicked.connect(sort_table) #Кнопка сортировки столбцов
    ui.updateButton.clicked.connect(updateTable) #Кнопка обновление таблицы
    ui.pushButton.clicked.connect(otherWindow) #Подключение к кнопке открытие нового окна на добавление новой карточки
    ui.searchButton.clicked.connect(lambda sh, sql_search=True: updateTable(sql_search)) #Кнопка для поиска пациента

    sys.exit(app.exec())

if __name__ == '__main__':
    with sqlite3.connect('data_bases/data.db') as db:
        cursor = db.cursor()
        katalog()