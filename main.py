from PyQt5 import QtCore, QtGui, QtWidgets

from MainForm import Ui_MainWindow
from case_record import Ui_Dialog
from case_record_edit import Ui_Dialog_edit
from diagnosis import Ui_Dialog_add_diag
import sqlite3
import sys
import json

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
    new_pat_id = result[0][0]+1
    ui.card_number.setText(f'№{new_pat_id}')

    def receive_data(): #Присвоение переменных
        fields = {
            "name": ui.pat_name.text(),
            "info": ui.general_chatacteristics.toPlainText(),
            "street": ui.street_name.text(),
            "affil": ui.affiliation.text(),
            "mobile": ui.mobile_1.text(),
            "mobile_2": ui.mobile_2.text(),
            "work_ph": ui.work_phone.text(),
            "home_ph": ui.home_phone.text(),
            "house_numb": ui.house_number.text(),
            "street_t": ui.comboBox_streets.currentText(),
            "manag": ui.manager.toPlainText(),
        }
        return fields

    def savePat(): #Внесение всей информации из ячеек в базу данных
        fields = receive_data()
        cursor.execute(f"""INSERT INTO patients(full_name, info, street, affiliation, mobile_1, mobile_2, w_phone, h_phone, house_numb, street_type, manager) 
                        VALUES("{fields['name']}", "{fields['info']}", "{fields['street']}", "{fields['affil']}", "{fields['mobile']}", 
                                "{fields['mobile_2']}", "{fields['work_ph']}", "{fields['home_ph']}", "{fields['house_numb']}", 
                                "{fields['street_t']}", "{fields['manag']}")""")
        db.commit()
        ui.add_to_diag_Button.setEnabled(True)
    def save_to_file_Pat(): #Сохранение всей информации пациента в формате json
        fields = receive_data()
        with open(f"save_cards/{fields['name']}.json", "w") as out_file:
            json.dump(fields, out_file, indent=4, sort_keys=True)

    def load_info_from_file(): #Загрузка из файла типа json всех данных и добавление их в ячейки
        with open(f"save_cards/Patient3.json.", "r") as out_file:
            data = json.load(out_file)

            """Заполнение ячеек данными полученых из файла"""
            ui.comboBox_streets.addItems(["вулиця", "провулок", "бульвар", "шоссе", "проспект"])
            ui.comboBox_streets.setCurrentText(data["street_t"])
            ui.street_name.setText(data["street"])
            ui.affiliation.setText(data["affil"])
            ui.mobile_1.setText(data["mobile"])
            ui.mobile_2.setText(data["mobile_2"])
            ui.work_phone.setText(data["work_ph"])
            ui.home_phone.setText(data["home_ph"])
            ui.general_chatacteristics.setText(data["info"])
            ui.house_number.setText(data["house_numb"])
            ui.pat_name.setText(data["name"])
            ui.manager.setText(data["manag"])

    ui.add_to_diag_Button.setEnabled(False)

    ui.add_to_diag_Button.clicked.connect(lambda sh, id=new_pat_id: add_new_diagnosis(id))
    ui.addButton.clicked.connect(load_info_from_file)
    ui.save_to_fileButton.clicked.connect(save_to_file_Pat)
    ui.saveButton.clicked.connect(savePat)#Кнопка сохранения информациия занесённой в ячейках в базу данных

def add_new_diagnosis(id): #Окно для добавления новых диагнозов
    global Dialog_add_diag
    Dialog_add_diag = QtWidgets.QDialog()
    ui = Ui_Dialog_add_diag()
    ui.setupUi(Dialog_add_diag)
    Dialog_add_diag.show()

    cursor.execute(f"SELECT full_name FROM patients WHERE patients_id = {id}")
    result = cursor.fetchall()

    ui.patient_add_diag.setReadOnly(True)
    ui.patient_add_diag.setText(result[0][0])

    def add_diagnosis_to_table():
        cursor.execute(f"""INSERT INTO diagnoses(date, apartment, patients_id, diagnosis)
                            VALUES("{ui.dateEdit_add_diag.dateTime().toString("dd.MM.yyyy")}", 
                            {ui.apart_add_diag.text()}, {id}, "{ui.diagnosis_add_diag.text()}")""")
        db.commit()
        Dialog_add_diag.close()
        diagnosesTable()

    ui.add_to_table_Button.clicked.connect(add_diagnosis_to_table)
def otherWindow_2(id): #Просмотр и редактирование карточки пациента
    global Dialog_edit
    global diagnosesTable
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
        cursor.execute(f"""SELECT date, apartment, full_name, diagnosis 
                            FROM patients join diagnoses using(patients_id) where patients_id = {id}""")
        result = cursor.fetchall()
        print(result)
        """Заполнение таблицы"""
        ui.tableWidget_diag_edit.setRowCount(len(result))
        for row, items in enumerate(result):
            for index, item in enumerate(items):
                ui.tableWidget_diag_edit.setItem(row, index, QtWidgets.QTableWidgetItem(str(item)))

    diagnosesTable()


    ui.add_to_diag_Button_2.clicked.connect(lambda sh, id_pat=id: add_new_diagnosis(id_pat)) #Кнопка для открытия нового окна для создания новой записи таблицы диагнозов
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