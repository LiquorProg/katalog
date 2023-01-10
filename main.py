from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QFileDialog

from MainForm import Ui_MainWindow
from case_record import Ui_CardNew
from case_record_edit import Ui_CardEdit
from case_record_file import Ui_CardFile
from diagnosis import Ui_Dialog_add_diag
from diagnosis_view import Ui_Dialog_view_diag
import sqlite3
import sys
import json


def otherWindow():  # Создание новой карточки пациента
    global CardNew
    CardNew = QtWidgets.QMainWindow()
    ui = Ui_CardNew()
    ui.setupUi(CardNew)
    CardNew.show()

    ui.comboBox_streets.addItems(
        ["вулиця", "провулок", "бульвар", "шоссе", "проспект"])  # Комбобокс с вариантами назв. улиц

    """Автонумирование для новой карточки пациента"""
    try:
        cursor.execute("select max(patients_id) from patients")
        result = cursor.fetchall()
        new_pat_id = result[0][0] + 1
    except:
        new_pat_id = 1

    global receive_data

    def receive_data():  # Присвоение переменных
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

    def savePat():  # Внесение всей информации из ячеек в базу данных
        fields = receive_data()
        cursor.execute(f"""INSERT INTO patients(full_name, info, street, affiliation, mobile_1, mobile_2, w_phone, h_phone, house_numb, street_type, manager)
                        VALUES("{fields['name']}", "{fields['info']}", "{fields['street']}", "{fields['affil']}", "{fields['mobile']}",
                                "{fields['mobile_2']}", "{fields['work_ph']}", "{fields['home_ph']}", "{fields['house_numb']}",
                                "{fields['street_t']}", "{fields['manag']}")""")
        db.commit()

        """Внесения в БД все записи из столбца с диагнозами"""
        if ui.tableWidget_diag.rowCount() > 0:
            for row in range(ui.tableWidget_diag.rowCount()):
                cursor.execute(f"""INSERT INTO diagnoses(date, apartment, patients_id, diagnosis)
                                            VALUES("{ui.tableWidget_diag.item(row, 0).text()}",
                                            "{ui.tableWidget_diag.item(row, 1).text()}", "{new_pat_id}",
                                            "{ui.tableWidget_diag.item(row, 3).text()}")""")
                db.commit()
        CardNew.close()

    def save_to_file_Pat():  # Сохранение всей информации пациента в формате json
        fields = receive_data()
        with open(f"save_cards/{fields['name']}({fields['street']}, {fields['house_numb']}).json", "w") as out_file:
            table = {}
            if ui.tableWidget_diag.rowCount() > 0:
                for row in range(ui.tableWidget_diag.rowCount()):
                    table[str(row)] = [
                        ui.tableWidget_diag.item(row, 0).text(),
                        int(ui.tableWidget_diag.item(row, 1).text()),
                        fields['name'],
                        ui.tableWidget_diag.item(row, 3).text()
                    ]
            json.dump([fields, table], out_file, indent=4, sort_keys=True)

    global add_new_row

    def add_new_row(date, apart, name, diag):  # Добавление строки в тоблицу диагнозов данные из окна
        row_count = ui.tableWidget_diag.rowCount()
        row_count += 1
        ui.tableWidget_diag.setRowCount(row_count)
        ui.tableWidget_diag.setItem(row_count - 1, 0, QtWidgets.QTableWidgetItem(str(date)))
        ui.tableWidget_diag.setItem(row_count - 1, 1, QtWidgets.QTableWidgetItem(str(apart)))
        ui.tableWidget_diag.setItem(row_count - 1, 2, QtWidgets.QTableWidgetItem(str(name)))
        ui.tableWidget_diag.setItem(row_count - 1, 3, QtWidgets.QTableWidgetItem(str(diag)))

    def del_row():  # Функция удаления строки
        row = ui.tableWidget_diag.currentRow()
        if row > -1:  # Если есть выделенная строка/элемент
            ui.tableWidget_diag.removeRow(row)
            ui.tableWidget_diag.selectionModel().clearCurrentIndex()  # этот вызов нужен для того, чтобы сбросить индекс выбранной строки

    def load_row_index(item: QtWidgets.QTableWidgetItem):  # Загрузка индекса выбраной строки и ее значения в окно ред. диагноза
        row = item.row()
        name = receive_data()
        fields = [
            ui.tableWidget_diag.item(row, 0).text(),
            ui.tableWidget_diag.item(row, 1).text(),
            name["name"],
            ui.tableWidget_diag.item(row, 3).text(),
        ]
        view_diagnosis(row, 2, fields)

    global edit_row
    def edit_row(row, items):  # Смена значений указаной строки в таблице диагнозов на отредактированные
        name = receive_data()
        ui.tableWidget_diag.setItem(row, 0, QtWidgets.QTableWidgetItem(items[0]))
        ui.tableWidget_diag.setItem(row, 1, QtWidgets.QTableWidgetItem(items[1]))
        ui.tableWidget_diag.setItem(row, 2, QtWidgets.QTableWidgetItem(name["name"]))
        ui.tableWidget_diag.setItem(row, 3, QtWidgets.QTableWidgetItem(items[2]))

    ui.tableWidget_diag.doubleClicked.connect(load_row_index)  # Открытие окна ред. диагноза на двойное нажатие на ячейку таблицы
    ui.del_from_diag_Button.clicked.connect(del_row)  # Кнопка удаления строки
    ui.add_to_diag_Button.clicked.connect(
        lambda sh, window=1: add_new_diagnosis(window))  # Кнопка открытия окна с полями для заполнения диагноза
    ui.save_to_fileButton.clicked.connect(save_to_file_Pat)  # Кнопка сохранения данных из ячеек в виде файла
    ui.saveButton.clicked.connect(savePat)  # Кнопка сохранения информациия занесённой в ячейках в базу данных


def add_new_diagnosis(window, name='', id=None):  # Окно для добавления новых диагнозов
    global Dialog_add_diag
    Dialog_add_diag = QtWidgets.QDialog()
    ui = Ui_Dialog_add_diag()
    ui.setupUi(Dialog_add_diag)
    Dialog_add_diag.show()

    """Разный метод присвоения имени в зависимости от окна в котором мы находимся"""
    if window == 1:
        fields = receive_data()
        ui.patient_add_diag.setText(fields["name"])
    elif window == 2:
        ui.patient_add_diag.setText(name)
    else:
        fields = receive_data_file()
        ui.patient_add_diag.setText(fields["name"])

    ui.patient_add_diag.setReadOnly(True)

    def add_diagnosis_to_table():  # Передача всех данных из ячеек в зависимости от окна в котором мы находимся
        if window == 1:
            ui.patient_add_diag.setText(fields["name"])
            add_new_row(ui.dateEdit_add_diag.dateTime().toString("dd.MM.yyyy"), ui.apart_add_diag.text(),
                        fields["name"], ui.diagnosis_add_diag.toPlainText())
        elif window == 2:
            ui.patient_add_diag.setText(name)
            cursor.execute(f"""INSERT INTO diagnoses(date, apartment, patients_id, diagnosis)
                                            VALUES("{ui.dateEdit_add_diag.dateTime().toString("dd.MM.yyyy")}",
                                                    "{ui.apart_add_diag.text()}", "{id}",
                                                    "{ui.diagnosis_add_diag.toPlainText()}")""")
            db.commit()
            diagnosesTable()  # Обновление таблицы после создания нового диагноза

        else:
            ui.patient_add_diag.setText(fields["name"])
            add_new_row_file(ui.dateEdit_add_diag.dateTime().toString("dd.MM.yyyy"), ui.apart_add_diag.text(),
                             fields["name"], ui.diagnosis_add_diag.toPlainText())
        Dialog_add_diag.close()

    ui.add_to_table_Button.clicked.connect(add_diagnosis_to_table)


def view_diagnosis(diag_id, window=1, fields=None):  # Просмотр и редактирование диагноза из таблицы диагнозов
    global Dialog_view_diag
    Dialog_view_diag = QtWidgets.QDialog()
    ui = Ui_Dialog_view_diag()
    ui.setupUi(Dialog_view_diag)
    Dialog_view_diag.show()

    ui.patient_view_diag.setReadOnly(True)

    """Заполнение ячеек данными в зависимости от текущего окна"""
    if window == 1:
        """Получение всей инф. об диагнозе из таблицы БД"""
        cursor.execute(
            f"SELECT date, apartment, full_name, diagnosis FROM patients join diagnoses using(patients_id) WHERE diagnosis_id = {diag_id}")
        result = cursor.fetchall()

        """Заполнение ячеек данными полученых из БД"""
        date = result[0][0].split('.')
        ui.dateEdit_view_diag.setDate(QDate(int(date[2]), int(date[1]), int(date[0])))
        ui.apart_view_diag.setText(str(result[0][1]))
        ui.patient_view_diag.setText(str(result[0][2]))
        ui.diagnosis_view_diag.setText(str(result[0][3]))

    else:
        date = fields[0].split('.')
        ui.dateEdit_view_diag.setDate(QDate(int(date[2]), int(date[1]), int(date[0])))
        ui.apart_view_diag.setText(fields[1])
        ui.patient_view_diag.setText(fields[2])
        ui.diagnosis_view_diag.setText(fields[3])

    def switch(status=True):  # Функция для переключения статуса виджетов
        if status:
            ui.saveButton_view.setEnabled(False)
        else:
            ui.saveButton_view.setEnabled(True)
        ui.apart_view_diag.setReadOnly(status)
        ui.diagnosis_view_diag.setReadOnly(status)

    def save_changes():  # Функция сохранения отредактированой информации в таблицу диагнозов, способ сохранения зависит от текущего окна
        if window == 1:
            cursor.execute(
                f"""UPDATE diagnoses SET date='{ui.dateEdit_view_diag.dateTime().toString("dd.MM.yyyy")}',
                        apartment='{ui.apart_view_diag.text()}', diagnosis='{ui.diagnosis_view_diag.toPlainText()}' 
                        WHERE diagnosis_id={diag_id} """)
            db.commit()
            diagnosesTable()
        else:
            items = [
                ui.dateEdit_view_diag.dateTime().toString("dd.MM.yyyy"),
                ui.apart_view_diag.text(),
                ui.diagnosis_view_diag.toPlainText()
            ]
            if window == 2:
                edit_row(diag_id, items)
            else:
                edit_row_file(diag_id, items)

        Dialog_view_diag.close()

    switch()

    ui.editButton_view.clicked.connect(lambda sh, stat=False: switch(stat))
    ui.saveButton_view.clicked.connect(save_changes)


def otherWindow_2(id):  # Просмотр и редактирование карточки пациента
    global CardEdit
    CardEdit = QtWidgets.QMainWindow()
    ui = Ui_CardEdit()
    ui.setupUi(CardEdit)
    CardEdit.show()

    """Получение всей инф. об определенном пациенте из таблицы БД"""
    cursor.execute(f"SELECT * FROM patients WHERE patients_id = {id}")
    result = cursor.fetchall()

    def load_index(index: QtCore.QModelIndex):  # Функция для передачи id диагноза в окно просмотра диагноза
        diag_id = index.siblingAtColumn(4).data(QtCore.Qt.ItemDataRole.DisplayRole)
        view_diagnosis(diag_id)

    ui.tableWidget_diag_edit.hideColumn(4)  # Скрытие колонки с id диагнозов

    def switch(status=True):  # Функция для переключения статуса виджетов
        if not status:
            ui.comboBox_streets_2.clear()
            cursor.execute(f"SELECT * FROM patients WHERE patients_id = {id}")
            new_result = cursor.fetchall()
            ui.comboBox_streets_2.addItems(["вулиця", "провулок", "бульвар", "шоссе", "проспект"])
            ui.comboBox_streets_2.setCurrentText(str(new_result[0][10]))
            ui.saveButton_2.setEnabled(True)
            ui.addButton_2.setEnabled(True)
            ui.save_to_fileButton_2.setEnabled(False)
            ui.editButton.setEnabled(False)
        else:
            ui.comboBox_streets_2.clear()
            cursor.execute(f"SELECT * FROM patients WHERE patients_id = {id}")
            new_result = cursor.fetchall()
            ui.comboBox_streets_2.addItems([str(new_result[0][10])])
            ui.editButton.setEnabled(True)
            ui.addButton_2.setEnabled(False)
            ui.tableWidget_diag_edit.doubleClicked.connect(load_index)

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

    def receive_data():  # Присвоение переменных
        fields = {
            "name": ui.pat_name_2.text(),
            "info": ui.general_chatacteristics_2.toPlainText(),
            "street": ui.street_name_2.text(),
            "affil": ui.affiliation_2.text(),
            "mobile": ui.mobile_1_2.text(),
            "mobile_2": ui.mobile_2_2.text(),
            "work_ph": ui.work_phone_2.text(),
            "home_ph": ui.home_phone_2.text(),
            "house_numb": ui.house_number_2.text(),
            "street_t": ui.comboBox_streets_2.currentText(),
            "manag": ui.manager_2.toPlainText(),
        }
        return fields

    def editPat():  # Занесение в БД отредактированные данные
        fields = receive_data()
        cursor.execute(
            f"""UPDATE patients SET full_name='{fields["name"]}', info='{fields["info"]}', street='{fields["street"]}', affiliation='{fields["affil"]}', 
                        mobile_1='{fields["mobile"]}', mobile_2='{fields["mobile_2"]}', w_phone='{fields["work_ph"]}', h_phone='{fields["home_ph"]}',
                        house_numb={fields["house_numb"]}, street_type='{fields["street_t"]}', manager='{fields["manag"]}' WHERE patients_id={id}""")
        db.commit()

        """Обратный переход в режим просмотра"""
        ui.saveButton_2.setEnabled(False)
        ui.addButton_2.setEnabled(False)
        ui.save_to_fileButton_2.setEnabled(True)
        ui.addButton_2.setEnabled(True)
        switch()
        diagnosesTable()

    switch()  # Установка виджетов в статус ReadOnly
    ui.saveButton_2.setEnabled(False)  # Кнопка сохранения не активна
    ui.addButton_2.setEnabled(False)  # Кнопка добавления доп. информации из файла не активна

    """Заполнение ячеек данными полученых из БД"""
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

    def sql_diagnosis():  # Запрос на получение всех данных о пациенте по диагнозам
        cursor.execute(f"""SELECT date, apartment, full_name, diagnosis, diagnosis_id
                                                FROM patients join diagnoses using(patients_id) where house_numb = {result[0][9]} and street = '{result[0][3]}' """)
        return cursor.fetchall()

    global diagnosesTable

    def diagnosesTable():  # Таблица с диагнозами
        result = sql_diagnosis()
        print(result)

        """Заполнение таблицы"""
        ui.tableWidget_diag_edit.setRowCount(len(result))
        for row, items in enumerate(result):
            for index, item in enumerate(items):
                ui.tableWidget_diag_edit.setItem(row, index, QtWidgets.QTableWidgetItem(str(item)))
        return len(result)

    diagnosesTable()  # Вызов функции для заполнения таблицы

    def save_to_file_Pat_edit():  # Сохранение всей информации пациента в формате json
        fields = receive_data()
        with open(f"save_cards/{fields['name']}({fields['street']}, {fields['house_numb']}).json", "w") as out_file:
            table = {}
            if ui.tableWidget_diag_edit.rowCount() > 0:
                for row in range(ui.tableWidget_diag_edit.rowCount()):
                    table[str(row)] = [
                        ui.tableWidget_diag_edit.item(row, 0).text(),
                        ui.tableWidget_diag_edit.item(row, 1).text(),
                        fields['name'],
                        ui.tableWidget_diag_edit.item(row, 3).text()
                    ]
            json.dump([fields, table], out_file, indent=4, sort_keys=True)

    def load_info_from_file_edit():  # Загрузка дополнительных данных из выбраного файла
        fname = QFileDialog().getOpenFileName(CardEdit, "Open", "save_cards", "Карточки формата json (*.json)")

        if fname[0]:
            with open(f"{fname[0]}", "r") as out_file:
                fields = receive_data()
                data = json.load(out_file)

                """Заполнение ячеек данными полученых из файла"""
                ui.general_chatacteristics_2.setText(fields["info"] + "\n" + data[0]["info"])
                row_count = ui.tableWidget_diag_edit.rowCount()

                if data[1]:
                    ui.tableWidget_diag_edit.setRowCount(row_count + len(data[1]))
                    for row, items in enumerate(data[1].values()):
                        for index, item in enumerate(items):
                            ui.tableWidget_diag_edit.setItem(row_count + row, index,
                                                             QtWidgets.QTableWidgetItem(str(item)))
                ui.addButton_2.setEnabled(False)

    ui.addButton_2.clicked.connect(load_info_from_file_edit)  # Кнопка добавления информации в карточку из файла
    ui.save_to_fileButton_2.clicked.connect(save_to_file_Pat_edit)  # Кнопка сохранения информации в виде файла
    ui.add_to_diag_Button_2.clicked.connect(
        lambda sh, window=2, name=str(result[0][1]), card_id=id: add_new_diagnosis(window, name,
                                                                                   card_id))  # Кнопка для открытия нового окна для создания новой записи таблицы диагнозов
    ui.editButton.clicked.connect(lambda sh, stat=False: switch(stat))  # Кнопка для редактирования ячеек
    ui.saveButton_2.clicked.connect(editPat)  # Кнопка сохранения


def otherWindow_3(file_data):  # Окно для просмотра файлов
    global CardFile
    CardFile = QtWidgets.QMainWindow()
    ui = Ui_CardFile()
    ui.setupUi(CardFile)
    CardFile.show()

    """Заполнение ячеек данными полученых из файла"""
    ui.error.setText("")
    ui.comboBox_streets_3.addItems(["вулиця", "провулок", "бульвар", "шоссе", "проспект"])
    ui.comboBox_streets_3.setCurrentText(file_data[0]["street_t"])
    ui.street_name_3.setText(file_data[0]["street"])
    ui.affiliation_3.setText(file_data[0]["affil"])
    ui.mobile_1_3.setText(file_data[0]["mobile"])
    ui.mobile_2_3.setText(file_data[0]["mobile_2"])
    ui.work_phone_3.setText(file_data[0]["work_ph"])
    ui.home_phone_3.setText(file_data[0]["home_ph"])
    ui.general_chatacteristics_3.setText(file_data[0]["info"])
    ui.house_number_3.setText(file_data[0]["house_numb"])
    ui.pat_name_3.setText(file_data[0]["name"])
    ui.manager_3.setText(file_data[0]["manag"])

    if file_data[1]:  # Проверка есть ли диагнозы, и заполнение таблицы
        ui.tableWidget_diag_file.setRowCount(len(file_data[1]))
        for row, items in enumerate(file_data[1].values()):
            for index, item in enumerate(items):
                ui.tableWidget_diag_file.setItem(row, index, QtWidgets.QTableWidgetItem(str(item)))

    """Автонумирование для новой карточки пациента"""
    cursor.execute("select max(patients_id) from patients")
    result = cursor.fetchall()
    new_pat_id = result[0][0] + 1

    global receive_data_file

    def receive_data_file():  # Присвоение переменных
        fields = {
            "name": ui.pat_name_3.text(),
            "info": ui.general_chatacteristics_3.toPlainText(),
            "street": ui.street_name_3.text(),
            "affil": ui.affiliation_3.text(),
            "mobile": ui.mobile_1_3.text(),
            "mobile_2": ui.mobile_2_3.text(),
            "work_ph": ui.work_phone_3.text(),
            "home_ph": ui.home_phone_3.text(),
            "house_numb": ui.house_number_3.text(),
            "street_t": ui.comboBox_streets_3.currentText(),
            "manag": ui.manager_3.toPlainText(),
        }
        return fields

    def savePat():  # Внесение всей информации из ячеек в базу данных
        fields = receive_data_file()
        cursor.execute(f"""INSERT INTO patients(full_name, info, street, affiliation, mobile_1, mobile_2, w_phone, h_phone, house_numb, street_type, manager)
                        VALUES("{fields['name']}", "{fields['info']}", "{fields['street']}", "{fields['affil']}", "{fields['mobile']}",
                                "{fields['mobile_2']}", "{fields['work_ph']}", "{fields['home_ph']}", "{fields['house_numb']}",
                                "{fields['street_t']}", "{fields['manag']}")""")
        db.commit()

        """Внесения в БД все записи из столбца с диагнозами"""
        if ui.tableWidget_diag_file.rowCount() > 0:
            for row in range(ui.tableWidget_diag_file.rowCount()):
                cursor.execute(f"""INSERT INTO diagnoses(date, apartment, patients_id, diagnosis)
                                            VALUES("{ui.tableWidget_diag_file.item(row, 0).text()}",
                                            "{ui.tableWidget_diag_file.item(row, 1).text()}", "{new_pat_id}",
                                            "{ui.tableWidget_diag_file.item(row, 3).text()}")""")
                db.commit()
        CardFile.close()

    global add_new_row_file

    def add_new_row_file(date, apart, name, diag):  # Добавление строки в тоблицу диагнозов данные из окна
        row_count = ui.tableWidget_diag_file.rowCount()
        row_count += 1
        ui.tableWidget_diag_file.setRowCount(row_count)
        ui.tableWidget_diag_file.setItem(row_count - 1, 0, QtWidgets.QTableWidgetItem(str(date)))
        ui.tableWidget_diag_file.setItem(row_count - 1, 1, QtWidgets.QTableWidgetItem(str(apart)))
        ui.tableWidget_diag_file.setItem(row_count - 1, 2, QtWidgets.QTableWidgetItem(str(name)))
        ui.tableWidget_diag_file.setItem(row_count - 1, 3, QtWidgets.QTableWidgetItem(str(diag)))

    def add_info_to_card():  # Добавления доп. данных из файла в выбранную карточку
        fields = receive_data_file()

        cursor.execute("select * from patients ")
        result = cursor.fetchall()

        pat_id = ui.curd_numberBox.value()

        if pat_id <= len(result):
            cursor.execute(f"select * from patients where patients_id = {pat_id}")
            result = cursor.fetchall()

            new_info = f"{result[0][2]}\n{fields['info']}"

            cursor.execute(
                f"""UPDATE patients SET info='{new_info}' WHERE patients_id={pat_id}""")
            db.commit()

            """Внесения в БД все записи из столбца с диагнозами"""
            if ui.tableWidget_diag_file.rowCount() > 0:
                for row in range(ui.tableWidget_diag_file.rowCount()):
                    cursor.execute(f"""INSERT INTO diagnoses(date, apartment, patients_id, diagnosis)
                                                        VALUES("{ui.tableWidget_diag_file.item(row, 0).text()}",
                                                        "{ui.tableWidget_diag_file.item(row, 1).text()}", "{pat_id}",
                                                        "{ui.tableWidget_diag_file.item(row, 3).text()}")""")
                    db.commit()
            CardFile.close()
        else:
            ui.error.setText("Такої картки нема")

    def del_row():
        row = ui.tableWidget_diag_file.currentRow()
        if row > -1:  # Если есть выделенная строка/элемент
            ui.tableWidget_diag_file.removeRow(row)
            ui.tableWidget_diag_file.selectionModel().clearCurrentIndex()  # этот вызов нужен для того, чтобы сбросить индекс выбранной строки

    def load_row_index(item: QtWidgets.QTableWidgetItem):  # Загрузка индекса выбраной строки и ее значения в окно ред. диагноза
        row = item.row()
        name = receive_data_file()
        fields = [
            ui.tableWidget_diag_file.item(row, 0).text(),
            ui.tableWidget_diag_file.item(row, 1).text(),
            name["name"],
            ui.tableWidget_diag_file.item(row, 3).text(),
        ]
        view_diagnosis(row, 3, fields)

    global edit_row_file
    def edit_row_file(row, items):  # Смена значений указаной строки в таблице диагнозов на отредактированные
        name = receive_data_file()
        ui.tableWidget_diag_file.setItem(row, 0, QtWidgets.QTableWidgetItem(items[0]))
        ui.tableWidget_diag_file.setItem(row, 1, QtWidgets.QTableWidgetItem(items[1]))
        ui.tableWidget_diag_file.setItem(row, 2, QtWidgets.QTableWidgetItem(name["name"]))
        ui.tableWidget_diag_file.setItem(row, 3, QtWidgets.QTableWidgetItem(items[2]))

    ui.tableWidget_diag_file.doubleClicked.connect(load_row_index)
    ui.del_from_diag_Button_2.clicked.connect(del_row)  # Кнопка удаления строки
    ui.add_to_diag_Button_3.clicked.connect(
        lambda sh, window=3: add_new_diagnosis(window))  # Кнопка добавления новой строки в табл. диагнозов
    ui.saveButton_3.clicked.connect(savePat)  # Кнопка сохранения карточки в картотеку
    ui.add_to_cardButton.clicked.connect(add_info_to_card)  # Кнопка добавления доп. информации в выбраную карточку


def katalog():  # Главная окно со списком карточек
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    def updateTable(sql_search=False):  # таблица со списком карточек пациентов
        if not sql_search:
            """SQL запрос на инф. из 4 столбцов для добавления в виджет без фильтров"""
            cursor.execute("SELECT patients_id, street_type, street, house_numb FROM patients")
            result = cursor.fetchall()
        else:
            """SQL запрос с фильтрами"""
            cursor.execute(
                f"""SELECT patients_id, street_type, street, house_numb FROM patients WHERE street LIKE '%{ui.search_street.text()}%'
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
                    ui.tableWidget.setItem(row, index, QtWidgets.QTableWidgetItem((' ' * 9 + str(item))[-9:]))
                else:
                    ui.tableWidget.setItem(row, index, QtWidgets.QTableWidgetItem(str(item)))

            """Создание и добавление кнопки в таблицу на открытие карточки пациента"""
            button = QtWidgets.QPushButton('Перегляд')
            button.clicked.connect(lambda sh, id=items[0]: otherWindow_2(id))
            ui.tableWidget.setCellWidget(row, 4, button)
        ui.tableWidget.setSortingEnabled(False)
        ui.sortButton.setEnabled(True)

    def sort_table():
        ui.tableWidget.setSortingEnabled(True)  # Сортировка столбцов
        ui.sortButton.setEnabled(False)

    updateTable()

    def load_info_from_file():  # Загрузка из файла типа json всех данных и добавление их в ячейки
        fname = QFileDialog().getOpenFileName(MainWindow, "Open", "save_cards", "Карточки формата json (*.json)")

        if fname[0]:
            with open(f"{fname[0]}", "r") as out_file:
                data = json.load(out_file)
                print(data)
                otherWindow_3(data)

    ui.view_fileButton.clicked.connect(load_info_from_file)  # Кнопка для просмотра файла
    ui.sortButton.clicked.connect(sort_table)  # Кнопка сортировки столбцов
    ui.updateButton.clicked.connect(updateTable)  # Кнопка обновление таблицы
    ui.pushButton.clicked.connect(otherWindow)  # Подключение к кнопке открытие нового окна на добавление новой карточки
    ui.searchButton.clicked.connect(lambda sh, sql_search=True: updateTable(sql_search))  # Кнопка для поиска пациента

    sys.exit(app.exec())


if __name__ == '__main__':
    with sqlite3.connect('data_bases/data.db') as db:
        cursor = db.cursor()
        katalog()
