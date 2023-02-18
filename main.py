import os
import sqlite3
import sys
import json
from contextlib import closing

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate, QRegExp
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QLabel, QWidget, QTableWidget
from PyQt5.QtGui import QPixmap, QRegExpValidator

from pyqt_files.MainForm import Ui_MainWindow
from pyqt_files.case_record import Ui_CardNew
from pyqt_files.case_record_edit import Ui_CardEdit
from pyqt_files.case_record_file import Ui_CardFile
from pyqt_files.diagnosis import Ui_Dialog_add_diag
from pyqt_files.diagnosis_view import Ui_Dialog_view_diag
from pyqt_files.photo import Ui_photo
from pyqt_files.address_lists import Ui_Address_listsWindow
from pyqt_files.error_window import Ui_errorWindow
from datetime import datetime


def otherWindow():  # Создание новой карточки пациента
    global CardNew
    CardNew = QtWidgets.QMainWindow()
    ui = Ui_CardNew()
    ui.setupUi(CardNew)
    CardNew.show()

    def clear_fields():  # Пустые поля для предупреждения
        ui.error_save.setText("")
        ui.error_save_file.setText("")
        ui.error_region.setText("")
        ui.error_district.setText("")
        ui.error_locality.setText("")
        ui.error_street.setText("")
        ui.error_house_numb.setText("")
    clear_fields()

    ui.comboBox_streets.addItems(["вулиця", "провулок", "бульвар", "шоссе", "проспект"])  # Комбобокс с типами улиц
    ui.comboBox_locality_type.addItems(["місто", "СМТ", "село", "селище", "хутір"])  # Комбобокс с типами населенных пунктов

    def address_dict_func():  # Словарь со списками названий таблиц, колонок и текущего адреса в комбобоксе для корректного SQL запроса
        address_dict = {
            "1": ["district_name", "districts", "region_id", "regions", "region_name", ui.comboBox_region_name.currentText()],
            "2": ["locality_name", "localities", "district_id", "districts", "district_name", ui.comboBox_district_name.currentText()],
            "3": ["street_name", "streets", "locality_id", "localities", "locality_name", ui.comboBox_locality_name.currentText()],
            "4": ["house_number", "house_numbers", "streets_id", "streets", "street_name", ui.comboBox_streets_name.currentText()],
        }
        return address_dict

    def sql_addresses(num):  # Запрос в БД на список адресов прикрепленных к одному адресу
        address_dict = address_dict_func()
        if int(num) - 1 == 0:
            cursor.execute(
                f"""SELECT {address_dict[num][0]}, {address_dict[num][2]} 
                        FROM {address_dict[num][1]} 
                        JOIN {address_dict[num][3]} using({address_dict[num][2]}) 
                        WHERE {address_dict[num][4]} = '{address_dict[num][5]}'""")
        else:
            cursor.execute(
                f"""SELECT {address_dict[num][0]}, {address_dict[num][2]} 
                                    FROM {address_dict[num][1]} 
                                    JOIN {address_dict[num][3]} using({address_dict[num][2]}) 
                                    JOIN {address_dict[str(int(num) - 1)][3]} using({address_dict[str(int(num) - 1)][2]}) 
                                    WHERE {address_dict[num][4]} = '{address_dict[num][5]}' AND
                                    {address_dict[str(int(num) - 1)][4]} = '{address_dict[str(int(num) - 1)][5]}' """)
        result = cursor.fetchall()
        return [i[0] for i in result]

    def set_address(nested_address, combobox, num):  # Установка списка адресов из БД, при смене другого адреса
        addresses_list = sql_addresses(num)  # Запрос в БД на список адресов
        if nested_address not in addresses_list and nested_address.strip() != "":  # Если адреса нет в БД, то добавить в список новый из ячейки
            addresses_list.append(nested_address)

        combobox.clear()
        combobox.addItems(addresses_list)
        combobox.setCurrentText(nested_address)

    """Установка списка адресов из БД, при смене другого адреса"""
    ui.comboBox_region_name.currentTextChanged.connect(
        lambda sh, nested_addr=ui.comboBox_district_name.currentText(), address_type=ui.comboBox_district_name, num="1":
        set_address(nested_addr, address_type, num))
    ui.comboBox_district_name.currentTextChanged.connect(
        lambda sh, nested_addr=ui.comboBox_locality_name.currentText(), address_type=ui.comboBox_locality_name, num="2":
        set_address(nested_addr, address_type, num))
    ui.comboBox_locality_name.currentTextChanged.connect(
        lambda sh, nested_addr=ui.comboBox_streets_name.currentText(), address_type=ui.comboBox_streets_name, num="3":
        set_address(nested_addr, address_type, num))
    ui.comboBox_streets_name.currentTextChanged.connect(
        lambda sh, nested_addr=ui.comboBox_house_number.currentText(), address_type=ui.comboBox_house_number, num="4":
        set_address(nested_addr, address_type, num))

    def list_sql_request(column, table):  # SQL запрос на название всех улиц, районов, областей и населенных пунктов сортировка и назначение этого списка на комбобокс
        cursor.execute(f"select {column} from {table}")
        result = cursor.fetchall()
        return sorted([i[0] for i in result])

    regions_list = list_sql_request("region_name", "regions")  # Список всех областей

    ui.comboBox_region_name.addItems(regions_list)  # Комбобокс с назв. областей

    """Автонумирование для новой карточки"""
    try:
        cursor.execute("select max(cards_id) from cards")
        result = cursor.fetchall()
        new_card_id = result[0][0] + 1
    except:
        new_card_id = 1

    global receive_data

    def receive_data():  # Присвоение переменных
        fields = {
            "info": ui.general_chatacteristics.toPlainText(),
            "street": ui.comboBox_streets_name.currentText(),
            "affil": ui.affiliation.text(),
            "mobile": ui.mobile_1.text(),
            "mobile_2": ui.mobile_2.text(),
            "work_ph": ui.work_phone.text(),
            "home_ph": ui.home_phone.text(),
            "house_numb": ui.comboBox_house_number.currentText(),
            "street_t": ui.comboBox_streets.currentText(),
            "manag": ui.manager.toPlainText(),
            "region_name": ui.comboBox_region_name.currentText(),
            "district_name": ui.comboBox_district_name.currentText(),
            "locality_t": ui.comboBox_locality_type.currentText(),
            "locality_name": ui.comboBox_locality_name.currentText(),
        }
        return fields

    def savePat():  # Внесение всей информации из ячеек в базу данных
        fields = receive_data()
        cursor.execute(f"""INSERT INTO cards(info, street, affiliation, mobile_1, mobile_2, w_phone, h_phone, 
                                                house_numb, street_type, manager, region, district, locality_type, locality)
                        VALUES( "{fields['info']}", "{fields['street']}", "{fields['affil']}", "{fields['mobile']}",
                                "{fields['mobile_2']}", "{fields['work_ph']}", "{fields['home_ph']}", "{fields['house_numb']}",
                                "{fields['street_t']}", "{fields['manag']}", "{fields['region_name']}", "{fields['district_name']}",
                                "{fields['locality_t']}", "{fields['locality_name']}")""")
        db.commit()

        def check_availability(field, lst, table, column):  # Если улицы, района, области и населенного пункта нет в базе данных, то она туда добавляется
            if field not in lst and field != '':
                cursor.execute(f"""INSERT INTO {table}({column}) VALUES("{field}")""")
                db.commit()

        check_availability(fields['region_name'], regions_list, "regions", "region_name")

        def address_availability_check(num, new_address):  # Проверка и внесение всех новых адресов
            address_dict = address_dict_func()

            if int(num) - 1 == 0:  # Проверка районов
                cursor.execute(
                    f"""SELECT {address_dict[num][2]} FROM {address_dict[num][3]} 
                                    WHERE {address_dict[num][4]} = '{address_dict[num][5]}'""")
                result = cursor.fetchall()
            else:  # Проверка последующих во вложенности адресов
                cursor.execute(
                    f"""SELECT {address_dict[num][2]} FROM {address_dict[num][3]} 
                                    JOIN {address_dict[str(int(num) - 1)][3]} USING({address_dict[str(int(num) - 1)][2]})
                                    WHERE {address_dict[num][4]} = '{address_dict[num][5]}' AND
                                    {address_dict[str(int(num) - 1)][4]} = '{address_dict[str(int(num) - 1)][5]}'""")
                result = cursor.fetchall()

            address_id = result[0][0]  # id адреса к которой мы прикрепим новый вложенный адрес

            address_list = sql_addresses(num)  # Запрос в БД на список адресов прикрепленных к одному объемлющему адресу

            if new_address.strip() not in address_list and new_address.strip() != '':  # Если адреса нет в базе данных, то он туда добавляется
                cursor.execute(
                    f"""INSERT INTO {address_dict[num][1]}({address_dict[num][0]}, {address_dict[num][2]}) 
                                VALUES("{new_address.strip()}", "{address_id}")""")
                db.commit()

        """Проверка и внесение всех новых адресов"""
        address_availability_check("1", fields["district_name"])
        address_availability_check("2", fields["locality_name"])
        address_availability_check("3", fields["street"])
        address_availability_check("4", fields["house_numb"])

        """Внесения в БД все записи из столбца с диагнозами"""
        if ui.tableWidget_diag.rowCount() > 0:
            for row in range(ui.tableWidget_diag.rowCount()):
                cursor.execute(f"""INSERT INTO diagnoses(date, apartment, patient_name, diagnosis, cards_id)
                                            VALUES("{ui.tableWidget_diag.item(row, 0).text()}",
                                                    "{ui.tableWidget_diag.item(row, 1).text()}", 
                                                    "{ui.tableWidget_diag.item(row, 2).text()}",
                                                    "{ui.tableWidget_diag.item(row, 3).text()}", "{new_card_id}")""")
                db.commit()
        CardNew.close()

    def save_to_file_Pat():  # Сохранение всей информации пациента в формате json
        fields = receive_data()
        with open(f"save_cards/{fields['street_t']} {fields['street']}, {fields['house_numb']}.json", "w") as out_file:
            table = {}
            if ui.tableWidget_diag.rowCount() > 0:
                for row in range(ui.tableWidget_diag.rowCount()):
                    table[str(row)] = [
                        ui.tableWidget_diag.item(row, 0).text(),
                        ui.tableWidget_diag.item(row, 1).text(),
                        ui.tableWidget_diag.item(row, 2).text(),
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
        fields = [
            ui.tableWidget_diag.item(row, 0).text(),
            ui.tableWidget_diag.item(row, 1).text(),
            ui.tableWidget_diag.item(row, 2).text(),
            ui.tableWidget_diag.item(row, 3).text(),
        ]
        view_diagnosis(row, 2, fields)

    global edit_row

    def edit_row(row, items):  # Смена значений указанной строки в таблице диагнозов на отредактированные
        ui.tableWidget_diag.setItem(row, 0, QtWidgets.QTableWidgetItem(items[0]))
        ui.tableWidget_diag.setItem(row, 1, QtWidgets.QTableWidgetItem(items[1]))
        ui.tableWidget_diag.setItem(row, 2, QtWidgets.QTableWidgetItem(items[2]))
        ui.tableWidget_diag.setItem(row, 3, QtWidgets.QTableWidgetItem(items[3]))

    global entering_additional_information
    def entering_additional_information(pat_id):  # Добавление доп. информации(общей характиристики и диагнозов)
        fields = receive_data()

        cursor.execute(f"select * from cards where cards_id = {pat_id}")
        result = cursor.fetchall()

        """Проверка есть ли в общей характеристике текст"""
        if fields['info'].strip() != "" and result[0][1].strip() != "":
            new_info = f"{result[0][1]}\n{fields['info']}"
        elif result[0][1].strip() == "" and fields['info'].strip() != "":
            new_info = fields['info']
        else:
            new_info = result[0][1]


        cursor.execute(
            f"""UPDATE cards SET info='{new_info}' WHERE cards_id={pat_id}""")
        db.commit()

        """Внесения в БД все записи из столбца с диагнозами"""
        if ui.tableWidget_diag.rowCount() > 0:
            for row in range(ui.tableWidget_diag.rowCount()):
                cursor.execute(f"""INSERT INTO diagnoses(date, apartment, patient_name, diagnosis, cards_id)
                                                            VALUES("{ui.tableWidget_diag.item(row, 0).text()}",
                                                            "{ui.tableWidget_diag.item(row, 1).text()}", 
                                                            "{ui.tableWidget_diag.item(row, 2).text()}",
                                                            "{ui.tableWidget_diag.item(row, 3).text()}", "{pat_id}")""")
                db.commit()
        CardNew.close()

    def field_validation(button):  # Проверка обязательных полей на наличие текста в них
        check_lst = []
        def check(combobox, error):
            if combobox.currentText().strip() == "":
                error.setText("Заповніть поле!")
                ui.error_save.setText("Заповніть поля!")
                check_lst.append(False)
            else:
                check_lst.append(True)

        """Проверка всех полей"""
        check(ui.comboBox_region_name, ui.error_region)
        check(ui.comboBox_district_name, ui.error_district)
        check(ui.comboBox_locality_name, ui.error_locality)
        check(ui.comboBox_streets_name, ui.error_street)
        check(ui.comboBox_house_number, ui.error_house_numb)

        if all(check_lst):
            if button == 1:
                checking_the_address_for_availability()
            else:
                save_to_file_Pat()
            clear_fields()

    def checking_the_address_for_availability():  # Проверка при попытке добавить новую карточку, адреса, существует ли уже карточка по такому же адресу
        fields = receive_data()
        current_address = ".".join([
            fields["region_name"], fields["district_name"],
            fields["locality_name"], fields["street"],
            fields["house_numb"]
        ])

        cursor.execute(
            f"""SELECT region, district, locality, street, house_numb, cards_id FROM cards """)
        result = cursor.fetchall()
        all_existing_addresses = {".".join(addresses[:-1]): f"{addresses[-1]}" for addresses in result}
        print(all_existing_addresses)

        if current_address in all_existing_addresses:  # Если карточка с таким адресом уже существует, то вызывается окно предупреждения, если нет то карточка просто добавляеться в картотеку
            id = all_existing_addresses[current_address]
            print(id)
            error_window(
                f"Картка по цій адресі вже існує у картотеці! Її номер - {id}.\nЗагальна характеристика і діагнози додадуться в неї.", 2, id)
        else:
            savePat()


    ui.tableWidget_diag.doubleClicked.connect(load_row_index)  # Открытие окна ред. диагноза на двойное нажатие на ячейку таблицы
    ui.del_from_diag_Button.clicked.connect(del_row)  # Кнопка удаления строки
    ui.add_to_diag_Button.clicked.connect(lambda sh, window=1: add_new_diagnosis(window))  # Кнопка открытия окна с полями для заполнения диагноза
    ui.save_to_fileButton.clicked.connect(lambda sh, button=2: field_validation(button))  # Кнопка сохранения данных из ячеек в виде файла
    ui.saveButton.clicked.connect(lambda sh, button=1: field_validation(button))  # Кнопка сохранения информациия занесённой в ячейках в базу данных


def add_new_diagnosis(window, name='', id=None):  # Окно для добавления новых диагнозов
    global Dialog_add_diag
    Dialog_add_diag = QtWidgets.QDialog()
    ui = Ui_Dialog_add_diag()
    ui.setupUi(Dialog_add_diag)
    Dialog_add_diag.show()

    """Подвязка текущего времени к созданию нового диагноза"""
    current_datetime = datetime.now()
    date = QDate(int(current_datetime.year), int(current_datetime.month), int(current_datetime.day))
    ui.dateEdit_add_diag.setDate(date)

    def add_diagnosis_to_table():  # Передача всех данных из ячеек в зависимости от окна в котором мы находимся
        if window == 1:
            add_new_row(ui.dateEdit_add_diag.dateTime().toString("dd.MM.yyyy"), ui.apart_add_diag.text(),
                        ui.patient_add_diag.text(), ui.diagnosis_add_diag.toPlainText())
        elif window == 2:
            cursor.execute(f"""INSERT INTO diagnoses(date, apartment, patient_name, diagnosis, cards_id)
                                            VALUES("{ui.dateEdit_add_diag.dateTime().toString("dd.MM.yyyy")}",
                                                    "{ui.apart_add_diag.text()}", "{ui.patient_add_diag.text()}",
                                                    "{ui.diagnosis_add_diag.toPlainText()}", "{id}")""")
            db.commit()
            diagnosesTable()  # Обновление таблицы после создания нового диагноза

        else:
            add_new_row_file(ui.dateEdit_add_diag.dateTime().toString("dd.MM.yyyy"), ui.apart_add_diag.text(),
                             ui.patient_add_diag.text(), ui.diagnosis_add_diag.toPlainText())
        Dialog_add_diag.close()

    ui.add_to_table_Button.clicked.connect(add_diagnosis_to_table)


def view_diagnosis(diag_id, window=1, fields=None):  # Просмотр и редактирование диагноза из таблицы диагнозов
    global Dialog_view_diag
    Dialog_view_diag = QtWidgets.QDialog()
    ui = Ui_Dialog_view_diag()
    ui.setupUi(Dialog_view_diag)
    Dialog_view_diag.show()

    """Заполнение ячеек данными в зависимости от текущего окна"""
    if window == 1:
        """Получение всей инф. об диагнозе из таблицы БД"""
        cursor.execute(
            f"SELECT date, apartment, patient_name, diagnosis FROM diagnoses WHERE diagnosis_id = {diag_id}")
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
        ui.patient_view_diag.setReadOnly(status)

    def save_changes():  # Функция сохранения отредактированой информации в таблицу диагнозов, способ сохранения зависит от текущего окна
        if window == 1:
            cursor.execute(
                f"""UPDATE diagnoses SET date='{ui.dateEdit_view_diag.dateTime().toString("dd.MM.yyyy")}',
                         apartment='{ui.apart_view_diag.text()}', patient_name='{ui.patient_view_diag.text()}',
                        diagnosis='{ui.diagnosis_view_diag.toPlainText()}' WHERE diagnosis_id={diag_id} """)
            db.commit()
            diagnosesTable()
        else:
            items = [
                ui.dateEdit_view_diag.dateTime().toString("dd.MM.yyyy"),
                ui.apart_view_diag.text(),
                ui.patient_view_diag.text(),
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

    def clear_fields():  # Очистка всех полей для предупреждения
        ui.error_save.setText("")
        ui.error_save_file.setText("")
        ui.error_region.setText("")
        ui.error_district.setText("")
        ui.error_locality.setText("")
        ui.error_street.setText("")
        ui.error_house_numb.setText("")
    clear_fields()

    """Получение всей инф. об определенном пациенте из таблицы БД"""
    def getting_all_info():
        cursor.execute(f"SELECT * FROM cards WHERE cards_id = {id}")
        return cursor.fetchall()

    result = getting_all_info()

    def load_index(index: QtCore.QModelIndex):  # Функция для передачи id диагноза в окно просмотра диагноза
        diag_id = index.siblingAtColumn(4).data(QtCore.Qt.ItemDataRole.DisplayRole)
        view_diagnosis(diag_id)

    ui.tableWidget_diag_edit.hideColumn(4)  # Скрытие колонки с id диагнозов

    def address_dict_func():  # Словарь со списками названий таблиц, колонок и текущего адреса в комбобоксе для корректного SQL запроса
        address_dict = {
            "1": ["district_name", "districts", "region_id", "regions", "region_name", ui.comboBox_region_name_2.currentText()],
            "2": ["locality_name", "localities", "district_id", "districts", "district_name", ui.comboBox_district_name_2.currentText()],
            "3": ["street_name", "streets", "locality_id", "localities", "locality_name", ui.comboBox_locality_name_2.currentText()],
            "4": ["house_number", "house_numbers", "streets_id", "streets", "street_name", ui.comboBox_streets_name_2.currentText()],
        }
        return address_dict

    def sql_addresses(num):  # Запрос в БД на список адресов прикрепленных к одному адресу
        address_dict = address_dict_func()
        if int(num) - 1 == 0:
            cursor.execute(
                f"""SELECT {address_dict[num][0]}, {address_dict[num][2]} 
                        FROM {address_dict[num][1]} 
                        JOIN {address_dict[num][3]} using({address_dict[num][2]}) 
                        WHERE {address_dict[num][4]} = '{address_dict[num][5]}'""")
        else:
            cursor.execute(
                f"""SELECT {address_dict[num][0]}, {address_dict[num][2]} 
                                    FROM {address_dict[num][1]} 
                                    JOIN {address_dict[num][3]} using({address_dict[num][2]}) 
                                    JOIN {address_dict[str(int(num) - 1)][3]} using({address_dict[str(int(num) - 1)][2]}) 
                                    WHERE {address_dict[num][4]} = '{address_dict[num][5]}' AND
                                    {address_dict[str(int(num) - 1)][4]} = '{address_dict[str(int(num) - 1)][5]}' """)
        result = cursor.fetchall()
        return [i[0] for i in result]

    def set_address(nested_address, combobox, num):  # Установка списка адресов из БД, при смене другого адреса
        addresses_list = sql_addresses(num)  # Запрос в БД на список адресов
        if nested_address not in addresses_list and nested_address.strip() != "":  # Если адреса нет в БД, то добавить в список новый из ячейки
            addresses_list.append(nested_address)

        combobox.clear()
        combobox.addItems(addresses_list)
        combobox.setCurrentText(nested_address)

    def list_sql_request(column, table):  # SQL запрос на название областей, сортировка и назначение этого списка на комбобокс
        cursor.execute(f"select {column} from {table}")
        result = cursor.fetchall()
        return sorted([i[0] for i in result])

    def check_availability_bd(lst, data):  # Если улицы нет в БД, то добавить в список новую из таблицы пациента
        if data not in lst and data != "":
            lst.append(data)

    def switch(status=True):  # Функция для переключения статуса виджетов
        if not status:
            ui.comboBox_streets_2.clear()
            ui.comboBox_locality_type_2.clear()
            ui.cancelButton.setStyleSheet("background-color: rgb(255, 49, 52)")
            ui.cancelButton.setEnabled(True)
            cursor.execute(f"SELECT * FROM cards WHERE cards_id = {id}")
            new_result = cursor.fetchall()

            ui.comboBox_streets_2.addItems(["вулиця", "провулок", "бульвар", "шоссе", "проспект"])  # Комбобокс с типами улиц
            ui.comboBox_locality_type_2.addItems(["місто", "СМТ", "село", "селище", "хутір"])  # Комбобокс с типами населенных пунктов
            ui.comboBox_streets_2.setCurrentText(str(new_result[0][9]))
            ui.comboBox_locality_type_2.setCurrentText(str(new_result[0][13]))

            regions_list = list_sql_request("region_name", "regions")  # Список всех областей

            check_availability_bd(regions_list, new_result[0][11].strip())  # Проверка на наличие области в БД

            ui.comboBox_region_name_2.clear()
            ui.comboBox_district_name_2.clear()
            ui.comboBox_locality_name_2.clear()
            ui.comboBox_streets_name_2.clear()
            ui.comboBox_house_number_2.clear()

            ui.comboBox_region_name_2.addItems(regions_list)  # Комбобокс с назв. областей

            ui.comboBox_streets_name_2.setEditable(True)
            ui.comboBox_region_name_2.setEditable(True)
            ui.comboBox_district_name_2.setEditable(True)
            ui.comboBox_locality_name_2.setEditable(True)
            ui.comboBox_house_number_2.setEditable(True)

            ui.saveButton_2.setEnabled(True)
            ui.addButton_2.setEnabled(True)
            ui.save_to_fileButton_2.setEnabled(False)
            ui.editButton.setEnabled(False)

            """Установка списка адресов из БД, при смене другого адреса"""
            ui.comboBox_region_name_2.currentTextChanged.connect(
                lambda sh, nested_addr=ui.comboBox_district_name_2.currentText(),
                       address_type=ui.comboBox_district_name_2, num="1":
                set_address(nested_addr, address_type, num))
            ui.comboBox_district_name_2.currentTextChanged.connect(
                lambda sh, nested_addr=ui.comboBox_locality_name_2.currentText(),
                       address_type=ui.comboBox_locality_name_2, num="2":
                set_address(nested_addr, address_type, num))
            ui.comboBox_locality_name_2.currentTextChanged.connect(
                lambda sh, nested_addr=ui.comboBox_streets_name_2.currentText(),
                       address_type=ui.comboBox_streets_name_2, num="3":
                set_address(nested_addr, address_type, num))
            ui.comboBox_streets_name_2.currentTextChanged.connect(
                lambda sh, nested_addr=ui.comboBox_house_number_2.currentText(),
                       address_type=ui.comboBox_house_number_2, num="4":
                set_address(nested_addr, address_type, num))

            ui.comboBox_region_name_2.setCurrentText(str(new_result[0][11]))
            ui.comboBox_district_name_2.setCurrentText(str(new_result[0][12]))
            ui.comboBox_locality_name_2.setCurrentText(str(new_result[0][14]))
            ui.comboBox_streets_name_2.setCurrentText(str(new_result[0][2]))
            ui.comboBox_house_number_2.setCurrentText(str(new_result[0][8]))
        else:
            ui.cancelButton.setEnabled(False)
            ui.cancelButton.setStyleSheet("background-color: rgb(255, 123, 123)")

            ui.comboBox_streets_2.clear()
            ui.comboBox_streets_name_2.clear()
            ui.comboBox_region_name_2.clear()
            ui.comboBox_district_name_2.clear()
            ui.comboBox_locality_type_2.clear()
            ui.comboBox_locality_name_2.clear()
            ui.comboBox_house_number_2.clear()

            cursor.execute(f"SELECT * FROM cards WHERE cards_id = {id}")
            new_result = cursor.fetchall()

            ui.comboBox_streets_2.addItems([str(new_result[0][9])])
            ui.comboBox_streets_name_2.addItems([str(new_result[0][2])])
            ui.comboBox_region_name_2.addItems([str(new_result[0][11])])
            ui.comboBox_district_name_2.addItems([str(new_result[0][12])])
            ui.comboBox_locality_type_2.addItems([str(new_result[0][13])])
            ui.comboBox_locality_name_2.addItems([str(new_result[0][14])])
            ui.comboBox_house_number_2.addItems([str(new_result[0][8])])
            ui.comboBox_streets_name_2.setEditable(False)
            ui.comboBox_region_name_2.setEditable(False)
            ui.comboBox_district_name_2.setEditable(False)
            ui.comboBox_locality_type_2.setEditable(False)
            ui.comboBox_locality_name_2.setEditable(False)
            ui.comboBox_house_number_2.setEditable(False)
            ui.editButton.setEnabled(True)
            ui.addButton_2.setEnabled(False)
            ui.tableWidget_diag_edit.doubleClicked.connect(load_index)

        ui.affiliation_2.setReadOnly(status)
        ui.mobile_1_2.setReadOnly(status)
        ui.mobile_2_2.setReadOnly(status)
        ui.work_phone_2.setReadOnly(status)
        ui.home_phone_2.setReadOnly(status)
        ui.general_chatacteristics_2.setReadOnly(status)
        ui.manager_2.setReadOnly(status)

    def receive_data():  # Присвоение переменных
        fields = {
            "info": ui.general_chatacteristics_2.toPlainText(),
            "street": ui.comboBox_streets_name_2.currentText(),
            "affil": ui.affiliation_2.text(),
            "mobile": ui.mobile_1_2.text(),
            "mobile_2": ui.mobile_2_2.text(),
            "work_ph": ui.work_phone_2.text(),
            "home_ph": ui.home_phone_2.text(),
            "house_numb": ui.comboBox_house_number_2.currentText(),
            "street_t": ui.comboBox_streets_2.currentText(),
            "manag": ui.manager_2.toPlainText(),
            "region_name": ui.comboBox_region_name_2.currentText(),
            "district_name": ui.comboBox_district_name_2.currentText(),
            "locality_t": ui.comboBox_locality_type_2.currentText(),
            "locality_name": ui.comboBox_locality_name_2.currentText(),
        }
        return fields

    def editPat():  # Занесение в БД отредактированные данные
        fields = receive_data()
        cursor.execute(
            f"""UPDATE cards SET info='{fields["info"]}', street='{fields["street"]}', affiliation='{fields["affil"]}', 
                        mobile_1='{fields["mobile"]}', mobile_2='{fields["mobile_2"]}', w_phone='{fields["work_ph"]}', h_phone='{fields["home_ph"]}',
                        house_numb='{fields["house_numb"]}', street_type='{fields["street_t"]}', manager='{fields["manag"]}', region='{fields['region_name']}', 
                        district='{fields['district_name']}', locality_type='{fields['locality_t']}', locality='{fields['locality_name']}' WHERE cards_id={id}""")
        db.commit()

        def check_availability(field, lst, table, column):  # Если области нет в базе данных, то она туда добавляется
            if field not in lst and field != '':
                cursor.execute(f"""INSERT INTO {table}({column}) VALUES("{field}")""")
                db.commit()

        regions_list = list_sql_request("region_name", "regions")  # Запрос в БД на список областей

        check_availability(fields['region_name'], regions_list, "regions", "region_name")

        def address_availability_check(num, new_address):  # Проверка и внесение всех новых адресов
            address_dict = address_dict_func()

            if int(num) - 1 == 0:
                cursor.execute(
                    f"""SELECT {address_dict[num][2]} FROM {address_dict[num][3]} 
                                    WHERE {address_dict[num][4]} = '{address_dict[num][5]}'""")
                result = cursor.fetchall()
            else:
                cursor.execute(
                    f"""SELECT {address_dict[num][2]} FROM {address_dict[num][3]} 
                                    JOIN {address_dict[str(int(num) - 1)][3]} USING({address_dict[str(int(num) - 1)][2]})
                                    WHERE {address_dict[num][4]} = '{address_dict[num][5]}' AND
                                    {address_dict[str(int(num) - 1)][4]} = '{address_dict[str(int(num) - 1)][5]}'""")
                result = cursor.fetchall()

            address_id = result[0][0]  # id адреса к которой мы прикрепим новый вложенный адрес

            adress_list = sql_addresses(num)  # Запрос в БД на список адресов прикрепленных к одному объемлющему адресу

            if new_address.strip() not in adress_list and new_address.strip() != '':  # Если адреса нет в базе данных, то он туда добавляется
                cursor.execute(
                    f"""INSERT INTO {address_dict[num][1]}({address_dict[num][0]}, {address_dict[num][2]}) 
                                VALUES("{new_address.strip()}", "{address_id}")""")
                db.commit()

        """Проверка и внесение всех новых адресов"""
        address_availability_check("1", fields["district_name"])
        address_availability_check("2", fields["locality_name"])
        address_availability_check("3", fields["street"])
        address_availability_check("4", fields["house_numb"])

        """Обратный переход в режим просмотра"""
        ui.saveButton_2.setEnabled(False)
        ui.addButton_2.setEnabled(False)
        ui.save_to_fileButton_2.setEnabled(True)
        ui.addButton_2.setEnabled(True)
        ui.comboBox_region_name_2.currentTextChanged.disconnect()
        ui.comboBox_district_name_2.currentTextChanged.disconnect()
        ui.comboBox_locality_name_2.currentTextChanged.disconnect()
        ui.comboBox_streets_name_2.currentTextChanged.disconnect()
        switch()
        diagnosesTable()

    switch()  # Установка виджетов в статус ReadOnly
    ui.saveButton_2.setEnabled(False)  # Кнопка сохранения не активна
    ui.addButton_2.setEnabled(False)  # Кнопка добавления доп. информации из файла не активна

    def filling_cells():  # Заполнение ячеек данными полученых из БД
        result = getting_all_info()

        ui.card_number_2.setText(f"№ {result[0][0]}")
        ui.affiliation_2.setText(str(result[0][3]))
        ui.mobile_1_2.setText(str(result[0][4]))
        ui.mobile_2_2.setText(str(result[0][5]))
        ui.work_phone_2.setText(str(result[0][6]))
        ui.home_phone_2.setText(str(result[0][7]))
        ui.general_chatacteristics_2.setText(str(result[0][1]))
        ui.manager_2.setText(str(result[0][10]))

    filling_cells()

    def sql_diagnosis():  # Запрос на получение всех данных о диагнозах пациентов

        cursor.execute(f"""SELECT date, apartment, patient_name, diagnosis, diagnosis_id
                                                FROM diagnoses where cards_id = '{id}' 
                                                AND patient_name LIKE '%{ui.pat_name_2.text()}%'""")
        return cursor.fetchall()

    global diagnosesTable

    def diagnosesTable():  # Таблица с диагнозами
        result = sql_diagnosis()
        sorted_result = sorted(result, key=lambda x: list(map(int, x[0].split('.')[::-1])), reverse=True)

        """Заполнение таблицы"""
        ui.tableWidget_diag_edit.setRowCount(len(sorted_result))
        for row, items in enumerate(sorted_result):
            for index, item in enumerate(items):
                ui.tableWidget_diag_edit.setItem(row, index, QtWidgets.QTableWidgetItem(str(item)))

    diagnosesTable()  # Вызов функции для заполнения таблицы

    ui.pat_name_2.textChanged.connect(diagnosesTable)  # Заполнение таблици при вводе имени пациента в ячейку для поиска пациента

    global deleting_patients_diagnosis

    def deleting_patients_diagnosis():  # Удаления выбранного диагноза
        row = ui.tableWidget_diag_edit.currentRow()
        if row > -1:  # Если есть выделенная строка/элемент
            diag_id = ui.tableWidget_diag_edit.item(row, 4).text()
            print(diag_id, row)
            cursor.execute(
                f"""DELETE FROM diagnoses WHERE diagnosis_id={diag_id}""")
            db.commit()
            diagnosesTable()

            ui.tableWidget_diag_edit.selectionModel().clearCurrentIndex()  # этот вызов нужен для того, чтобы сбросить индекс выбранной строки

    def save_to_file_Pat_edit():  # Сохранение всей информации в формате json
        fields = receive_data()
        with open(f"save_cards/{fields['street_t']} {fields['street']}, {fields['house_numb']}.json", "w") as out_file:
            table = {}
            if ui.tableWidget_diag_edit.rowCount() > 0:
                for row in range(ui.tableWidget_diag_edit.rowCount()):
                    table[str(row)] = [
                        ui.tableWidget_diag_edit.item(row, 0).text(),
                        ui.tableWidget_diag_edit.item(row, 1).text(),
                        ui.tableWidget_diag_edit.item(row, 2).text(),
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

    def cancel_changes():  # Обратный переход в режим просмотра
        ui.saveButton_2.setEnabled(False)
        ui.addButton_2.setEnabled(False)
        ui.save_to_fileButton_2.setEnabled(True)
        ui.addButton_2.setEnabled(True)
        ui.comboBox_region_name_2.currentTextChanged.disconnect()
        ui.comboBox_district_name_2.currentTextChanged.disconnect()
        ui.comboBox_locality_name_2.currentTextChanged.disconnect()
        ui.comboBox_streets_name_2.currentTextChanged.disconnect()
        filling_cells()
        clear_fields()
        switch()

    def field_validation():  # Проверка обязательных полей на наличие текста в них
        check_lst = []
        def check(combobox, error):
            if combobox.currentText().strip() == "":
                error.setText("Заповніть поле!")
                ui.error_save.setText("Заповніть поля!")
                check_lst.append(False)
            else:
                check_lst.append(True)
        check(ui.comboBox_region_name_2, ui.error_region)
        check(ui.comboBox_district_name_2, ui.error_district)
        check(ui.comboBox_locality_name_2, ui.error_locality)
        check(ui.comboBox_streets_name_2, ui.error_street)
        check(ui.comboBox_house_number_2, ui.error_house_numb)

        if all(check_lst):
            checking_the_address_for_availability()  # Проверка адреса
            clear_fields()

    def checking_the_address_for_availability():  # Проверка при попытке поменять адресс, существует ли уже карточка по такому же адресу, если есть, то вызвать ошибку
        fields = receive_data()
        current_address = ".".join([
            fields["region_name"], fields["district_name"],
            fields["locality_name"], fields["street"],
            fields["house_numb"]
        ])

        cursor.execute(
            f"""SELECT region, district, locality, street, house_numb, cards_id FROM cards WHERE cards_id <> {id}""")
        result = cursor.fetchall()
        all_existing_addresses = {".".join(addresses[:-1]): f"{addresses[-1]}" for addresses in result}
        print(all_existing_addresses)

        if current_address in all_existing_addresses:  # Если карточка с таким адресом уже существует, то вызывается окно предупреждения
            pat_id = all_existing_addresses[current_address]
            print(pat_id)
            error_window(
                f"Картка по цій адресі вже існує у картотеці! Її номер - {pat_id}.\nВідмініть зміни або запишіть нову адресу.", None, pat_id)
        else:
            editPat()  # Сохранение всех данных в БД

    ui.cancelButton.clicked.connect(cancel_changes)  # Кнопка отмены изменений и переход режим просмотра
    ui.photoButton.clicked.connect(lambda sh, card_id=id: photoWindow(card_id))  # Кнопка открытия папки ч фото пациентов
    ui.addButton_2.clicked.connect(load_info_from_file_edit)  # Кнопка добавления информации в карточку из файла
    ui.save_to_fileButton_2.clicked.connect(save_to_file_Pat_edit)  # Кнопка сохранения информации в виде файла
    ui.add_to_diag_Button.clicked.connect(
        lambda sh, window=2, name=str(result[0][1]), card_id=id: add_new_diagnosis(window, name, card_id))  # Кнопка для открытия нового окна для создания новой записи таблицы диагнозов
    ui.del_from_diag_Button.clicked.connect(
        lambda sh, txt=f"Діагноз видалится без можливості відновитись",
        type=4, thi=None: error_window(txt, type, thi))  # Кнопка для удаления диагнозов
    ui.editButton.clicked.connect(lambda sh, stat=False: switch(stat))  # Кнопка для редактирования ячеек
    ui.saveButton_2.clicked.connect(field_validation)  # Кнопка сохранения


def photoWindow(id):
    direct = f"photo_storage/patients(№{id})"  # Место хранения фотографий

    """Проверки на наличия папки пациента, если папки нет то создание ёё"""
    if not os.path.isdir(direct):
        os.mkdir(direct)

    fname = QFileDialog().getOpenFileName(CardEdit, "Фото", f"photo_storage/patients(№{id})",
                                          "Фотографии (*.png *.jpg *.bmp)")

    if fname[0]:
        global photo
        photo = QtWidgets.QDialog()
        ui = Ui_photo()
        ui.setupUi(photo)
        photo.show()
        pixmap = QPixmap(fname[0])

        ui.label.setPixmap(pixmap)
        ui.label.resize(pixmap.width(), pixmap.height())

        photo.resize(pixmap.width(), pixmap.height())


def otherWindow_3(file_data):  # Окно для просмотра файлов
    global CardFile
    CardFile = QtWidgets.QMainWindow()
    ui = Ui_CardFile()
    ui.setupUi(CardFile)
    CardFile.show()

    def clear_fields():  # Пустые поля для предупреждения
        ui.error.setText("")
        ui.error_save.setText("")
        ui.error_region.setText("")
        ui.error_district.setText("")
        ui.error_locality.setText("")
        ui.error_street.setText("")
        ui.error_house_numb.setText("")
        ui.error_save_file.setText("")
    clear_fields()

    ui.comboBox_streets_3.addItems(["вулиця", "провулок", "бульвар", "шоссе", "проспект"])  # Комбобокс с типами улиц
    ui.comboBox_locality_type_3.addItems(["місто", "СМТ", "село", "селище", "хутір"])  # Комбобокс с типами населенных пунктов

    def address_dict_func():  # Словарь со списками названий таблиц, колонок и текущего адреса в комбобоксе для корректного SQL запроса
        address_dict = {
            "1": ["district_name", "districts", "region_id", "regions", "region_name", ui.comboBox_region_name_3.currentText()],
            "2": ["locality_name", "localities", "district_id", "districts", "district_name", ui.comboBox_district_name_3.currentText()],
            "3": ["street_name", "streets", "locality_id", "localities", "locality_name", ui.comboBox_locality_name_3.currentText()],
            "4": ["house_number", "house_numbers", "streets_id", "streets", "street_name", ui.comboBox_streets_name_3.currentText()],
        }
        return address_dict

    def sql_addresses(num):  # Запрос в БД на список адресов прикрепленных к одному адресу
        address_dict = address_dict_func()
        if int(num)-1 == 0:
            cursor.execute(
                f"""SELECT {address_dict[num][0]}, {address_dict[num][2]} 
                        FROM {address_dict[num][1]} 
                        JOIN {address_dict[num][3]} using({address_dict[num][2]}) 
                        WHERE {address_dict[num][4]} = '{address_dict[num][5]}'""")
        else:
            cursor.execute(
                f"""SELECT {address_dict[num][0]}, {address_dict[num][2]} 
                                    FROM {address_dict[num][1]} 
                                    JOIN {address_dict[num][3]} using({address_dict[num][2]}) 
                                    JOIN {address_dict[str(int(num)-1)][3]} using({address_dict[str(int(num)-1)][2]}) 
                                    WHERE {address_dict[num][4]} = '{address_dict[num][5]}' AND
                                    {address_dict[str(int(num)-1)][4]} = '{address_dict[str(int(num)-1)][5]}' """)
        result = cursor.fetchall()
        return [i[0] for i in result]

    def set_address(nested_address, combobox, num):  # Установка списка адресов из БД, при смене другого адреса
        addresses_list = sql_addresses(num)  # Запрос в БД на список адресов
        if nested_address not in addresses_list and nested_address.strip() != "":  # Если адреса нет в БД, то добавить в список новый из ячейки
            addresses_list.append(nested_address)

        combobox.clear()
        combobox.addItems(addresses_list)
        combobox.setCurrentText(nested_address)

    """Установка списка адресов из БД, при смене другого адреса"""
    ui.comboBox_region_name_3.currentTextChanged.connect(
        lambda sh, nested_addr=ui.comboBox_district_name_3.currentText(), address_type=ui.comboBox_district_name_3, num="1":
        set_address(nested_addr, address_type, num))
    ui.comboBox_district_name_3.currentTextChanged.connect(
        lambda sh, nested_addr=ui.comboBox_locality_name_3.currentText(), address_type=ui.comboBox_locality_name_3, num="2":
        set_address(nested_addr, address_type, num))
    ui.comboBox_locality_name_3.currentTextChanged.connect(
        lambda sh, nested_addr=ui.comboBox_streets_name_3.currentText(), address_type=ui.comboBox_streets_name_3, num="3":
        set_address(nested_addr, address_type, num))
    ui.comboBox_streets_name_3.currentTextChanged.connect(
        lambda sh, nested_addr=ui.comboBox_house_number_3.currentText(), address_type=ui.comboBox_house_number_3, num="4":
        set_address(nested_addr, address_type, num))

    def list_sql_request(column, table):  # SQL запрос на название всех областей и сортировка и назначение этого списка на комбобокс
        cursor.execute(f"select {column} from {table}")
        result = cursor.fetchall()
        return sorted([i[0] for i in result])

    regions_list = list_sql_request("region_name", "regions")  # Список всех областей

    def check_availability_bd(lst, data):  # Если адреса нет в БД, то добавить в список новый из файла
        if data not in lst:
            lst.append(data)

    check_availability_bd(regions_list, file_data[0]["region_name"].strip())

    """Заполнение ячеек данными полученых из файла"""
    ui.comboBox_region_name_3.addItems(regions_list)
    ui.comboBox_region_name_3.setCurrentText(file_data[0]["region_name"])
    ui.comboBox_district_name_3.setCurrentText(file_data[0]["district_name"])
    ui.comboBox_locality_name_3.setCurrentText(file_data[0]["locality_name"])
    ui.comboBox_streets_name_3.setCurrentText(file_data[0]["street"])
    ui.comboBox_house_number_3.setCurrentText(file_data[0]["house_numb"])
    ui.comboBox_streets_3.setCurrentText(file_data[0]["street_t"])
    ui.comboBox_locality_type_3.setCurrentText(file_data[0]["locality_t"])
    ui.affiliation_3.setText(file_data[0]["affil"])
    ui.mobile_1_3.setText(file_data[0]["mobile"])
    ui.mobile_2_3.setText(file_data[0]["mobile_2"])
    ui.work_phone_3.setText(file_data[0]["work_ph"])
    ui.home_phone_3.setText(file_data[0]["home_ph"])
    ui.general_chatacteristics_3.setText(file_data[0]["info"])
    ui.manager_3.setText(file_data[0]["manag"])

    if file_data[1]:  # Проверка есть ли диагнозы, и заполнение таблицы
        ui.tableWidget_diag_file.setRowCount(len(file_data[1]))
        for row, items in enumerate(file_data[1].values()):
            for index, item in enumerate(items):
                ui.tableWidget_diag_file.setItem(row, index, QtWidgets.QTableWidgetItem(str(item)))

    """Автонумирование для новой карточки пациента"""
    try:
        cursor.execute("select max(cards_id) from cards")
        result = cursor.fetchall()
        new_pat_id = result[0][0] + 1
    except:
        new_pat_id = 1

    global receive_data_file

    def receive_data_file():  # Присвоение переменных
        fields = {
            "info": ui.general_chatacteristics_3.toPlainText(),
            "street": ui.comboBox_streets_name_3.currentText(),
            "affil": ui.affiliation_3.text(),
            "mobile": ui.mobile_1_3.text(),
            "mobile_2": ui.mobile_2_3.text(),
            "work_ph": ui.work_phone_3.text(),
            "home_ph": ui.home_phone_3.text(),
            "house_numb": ui.comboBox_house_number_3.currentText(),
            "street_t": ui.comboBox_streets_3.currentText(),
            "manag": ui.manager_3.toPlainText(),
            "region_name": ui.comboBox_region_name_3.currentText(),
            "district_name": ui.comboBox_district_name_3.currentText(),
            "locality_t": ui.comboBox_locality_type_3.currentText(),
            "locality_name": ui.comboBox_locality_name_3.currentText(),
        }
        return fields

    def savePat_file():  # Внесение всей информации из ячеек в базу данных
        fields = receive_data_file()
        cursor.execute(f"""INSERT INTO cards(info, street, affiliation, mobile_1, mobile_2, w_phone, h_phone, house_numb, 
                                                street_type, manager, region, district, locality_type, locality)
                        VALUES( "{fields['info']}", "{fields['street']}", "{fields['affil']}", "{fields['mobile']}",
                                "{fields['mobile_2']}", "{fields['work_ph']}", "{fields['home_ph']}", "{fields['house_numb']}",
                                "{fields['street_t']}", "{fields['manag']}", "{fields['region_name']}", "{fields['district_name']}",
                                "{fields['locality_t']}", "{fields['locality_name']}")""")
        db.commit()

        def check_availability(field, lst, table, column):  # Если улицы, района, области и населенного пункта нет в базе данных, то она туда добавляется
            if field not in lst and field != '':
                cursor.execute(f"""INSERT INTO {table}({column}) VALUES("{field}")""")
                db.commit()

        regions_list = list_sql_request("region_name", "regions")  # Запрос в БД на список областей

        check_availability(fields['region_name'], regions_list, "regions", "region_name")

        def address_availability_check(num, new_address):  # SQL запрос для получения id адреса, чтоб правильно добавить новый
            address_dict = address_dict_func()
            if int(num)-1 == 0:
                cursor.execute(
                    f"""SELECT {address_dict[num][2]} FROM {address_dict[num][3]} 
                                    WHERE {address_dict[num][4]} = '{address_dict[num][5]}'""")
                result = cursor.fetchall()
            else:
                cursor.execute(
                    f"""SELECT {address_dict[num][2]} FROM {address_dict[num][3]} 
                                    JOIN {address_dict[str(int(num)-1)][3]} USING({address_dict[str(int(num)-1)][2]})
                                    WHERE {address_dict[num][4]} = '{address_dict[num][5]}' AND
                                    {address_dict[str(int(num)-1)][4]} = '{address_dict[str(int(num)-1)][5]}'""")
                result = cursor.fetchall()
            address_id = result[0][0]  # id адреса к которой мы прикрепим новый вложенный адрес

            adress_list = sql_addresses(num)  # Запрос в БД на список адресов прикрепленных к одному объемлющему адресу

            if new_address.strip() not in adress_list and new_address.strip() != '':  # Если адреса нет в базе данных, то он туда добавляется
                cursor.execute(
                    f"""INSERT INTO {address_dict[num][1]}({address_dict[num][0]}, {address_dict[num][2]}) 
                                VALUES("{new_address.strip()}", "{address_id}")""")
                db.commit()
        """Проверка и внесение всех новых адресов"""
        address_availability_check("1", fields["district_name"])
        address_availability_check("2", fields["locality_name"])
        address_availability_check("3", fields["street"])
        address_availability_check("4", fields["house_numb"])

        """Внесения в БД все записи из столбца с диагнозами"""
        if ui.tableWidget_diag_file.rowCount() > 0:
            for row in range(ui.tableWidget_diag_file.rowCount()):
                cursor.execute(f"""INSERT INTO diagnoses(date, apartment, patient_name, diagnosis, cards_id)
                                            VALUES("{ui.tableWidget_diag_file.item(row, 0).text()}",
                                            "{ui.tableWidget_diag_file.item(row, 1).text()}", 
                                            "{ui.tableWidget_diag_file.item(row, 2).text()}",
                                            "{ui.tableWidget_diag_file.item(row, 3).text()}", "{new_pat_id}")""")
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

        cursor.execute("select * from cards")
        result = cursor.fetchall()

        pat_id = ui.curd_numberBox.value()

        if pat_id <= len(result):
            cursor.execute(f"select * from cards where cards_id = {pat_id}")
            result = cursor.fetchall()

            if fields['info'].strip() != "" and result[0][1].strip() != "":
                new_info = f"{result[0][1]}\n{fields['info']}"
            elif result[0][1].strip() == "" and fields['info'].strip() != "":
                new_info = fields['info']
            else:
                new_info = result[0][1]

            cursor.execute(
                f"""UPDATE cards SET info='{new_info}' WHERE cards_id={pat_id}""")
            db.commit()

            """Внесения в БД все записи из столбца с диагнозами"""
            if ui.tableWidget_diag_file.rowCount() > 0:
                for row in range(ui.tableWidget_diag_file.rowCount()):
                    cursor.execute(f"""INSERT INTO diagnoses(date, apartment, patient_name, diagnosis, cards_id)
                                                        VALUES("{ui.tableWidget_diag_file.item(row, 0).text()}",
                                                        "{ui.tableWidget_diag_file.item(row, 1).text()}", 
                                                        "{ui.tableWidget_diag_file.item(row, 2).text()}",
                                                        "{ui.tableWidget_diag_file.item(row, 3).text()}", "{pat_id}")""")
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
        fields = [
            ui.tableWidget_diag_file.item(row, 0).text(),
            ui.tableWidget_diag_file.item(row, 1).text(),
            ui.tableWidget_diag_file.item(row, 2).text(),
            ui.tableWidget_diag_file.item(row, 3).text(),
        ]
        view_diagnosis(row, 3, fields)

    global edit_row_file

    def edit_row_file(row, items):  # Смена значений указаной строки в таблице диагнозов на отредактированные
        ui.tableWidget_diag_file.setItem(row, 0, QtWidgets.QTableWidgetItem(items[0]))
        ui.tableWidget_diag_file.setItem(row, 1, QtWidgets.QTableWidgetItem(items[1]))
        ui.tableWidget_diag_file.setItem(row, 2, QtWidgets.QTableWidgetItem(items[2]))
        ui.tableWidget_diag_file.setItem(row, 3, QtWidgets.QTableWidgetItem(items[3]))

    global entering_additional_information_file
    def entering_additional_information_file(pat_id):
        fields = receive_data_file()

        cursor.execute(f"select * from cards where cards_id = {pat_id}")
        result = cursor.fetchall()

        if fields['info'].strip() != "" and result[0][1].strip() != "":
            new_info = f"{result[0][1]}\n{fields['info']}"
        elif result[0][1].strip() == "" and fields['info'].strip() != "":
            new_info = fields['info']
        else:
            new_info = result[0][1]


        cursor.execute(
            f"""UPDATE cards SET info='{new_info}' WHERE cards_id={pat_id}""")
        db.commit()

        """Внесения в БД все записи из столбца с диагнозами"""
        if ui.tableWidget_diag_file.rowCount() > 0:
            for row in range(ui.tableWidget_diag_file.rowCount()):
                cursor.execute(f"""INSERT INTO diagnoses(date, apartment, patient_name, diagnosis, cards_id)
                                                            VALUES("{ui.tableWidget_diag_file.item(row, 0).text()}",
                                                            "{ui.tableWidget_diag_file.item(row, 1).text()}", 
                                                            "{ui.tableWidget_diag_file.item(row, 2).text()}",
                                                            "{ui.tableWidget_diag_file.item(row, 3).text()}", "{pat_id}")""")
                db.commit()
        CardFile.close()

    def save_to_file_Pat_edit():  # Сохранение всей информации в формате json
        fields = receive_data_file()

        if "katalog.exe" in sys.argv[0]:
            path = sys.argv[0][:-12]
        else:
            path = sys.argv[0][:-8]

        with open(f"{path}\\save_cards\\{fields['street_t']} {fields['street']}, {fields['house_numb']}.json", "w") as out_file:
            table = {}
            if ui.tableWidget_diag_file.rowCount() > 0:
                for row in range(ui.tableWidget_diag_file.rowCount()):
                    table[str(row)] = [
                        ui.tableWidget_diag_file.item(row, 0).text(),
                        ui.tableWidget_diag_file.item(row, 1).text(),
                        ui.tableWidget_diag_file.item(row, 2).text(),
                        ui.tableWidget_diag_file.item(row, 3).text()
                    ]
            json.dump([fields, table], out_file, indent=4, sort_keys=True)
        CardFile.close()

    def field_validation(button):  # Проверка обязательных полей на наличие текста в них
        check_lst = []
        def check(combobox, error):
            if combobox.currentText().strip() == "":
                error.setText("Заповніть поле!")
                if button == 1:
                    ui.error_save.setText("Заповніть поля!")
                else:
                    ui.error_save_file.setText("Заповніть поля!")
                check_lst.append(False)
            else:
                check_lst.append(True)

        check(ui.comboBox_region_name_3, ui.error_region)
        check(ui.comboBox_district_name_3, ui.error_district)
        check(ui.comboBox_locality_name_3, ui.error_locality)
        check(ui.comboBox_streets_name_3, ui.error_street)
        check(ui.comboBox_house_number_3, ui.error_house_numb)

        if all(check_lst):
            if button == 1:
                checking_the_address_for_availability()  # Добавление доп информации в уже существующую карточку
            else:
                save_to_file_Pat_edit()  # Сохранение карточки в виде файла в папке save_cards
            clear_fields()

    def checking_the_address_for_availability():  # Проверка при попытке добавить новую карточку, адреса, существует ли уже карточка по такому же адресу
        fields = receive_data_file()
        current_address = ".".join([
            fields["region_name"], fields["district_name"],
            fields["locality_name"], fields["street"],
            fields["house_numb"]
        ])

        cursor.execute(
            f"""SELECT region, district, locality, street, house_numb, cards_id FROM cards """)
        result = cursor.fetchall()
        all_existing_addresses = {".".join(addresses[:-1]): f"{addresses[-1]}" for addresses in result}
        print(all_existing_addresses)

        if current_address in all_existing_addresses:  # Если карточка с таким адресом уже существует, то вызывается окно предупреждения, если нет то карточка просто добавляеться в картотеку
            id = all_existing_addresses[current_address]
            print(id)
            error_window(
                f"Картка по цій адресі вже існує у картотеці! Її номер - {id}.\nЗагальна характеристика і діагнози додадуться в неї.", 3, id)
        else:
            savePat_file()

    ui.save_fileButton.clicked.connect(lambda sh, button=2: field_validation(button))  # Кнопка сохранения карточки в виде файла
    ui.tableWidget_diag_file.doubleClicked.connect(load_row_index)  # Открытие окна ред. диагноза на двойное нажатие на ячейку таблицы
    ui.del_from_diag_Button_2.clicked.connect(del_row)  # Кнопка удаления строки
    ui.add_to_diag_Button_3.clicked.connect(lambda sh, window=3: add_new_diagnosis(window))  # Кнопка добавления новой строки в табл. диагнозов
    ui.saveButton_3.clicked.connect(lambda sh, button=1: field_validation(button))  # Кнопка сохранения карточки в картотеку
    ui.add_to_cardButton.clicked.connect(add_info_to_card)  # Кнопка добавления доп. информации в выбраную карточку


def address_lists():
    global Address_listsWindow
    Address_listsWindow = QtWidgets.QMainWindow()
    ui = Ui_Address_listsWindow()
    ui.setupUi(Address_listsWindow)
    Address_listsWindow.show()

    current_address = "Regions"  # Установка текущего адреса "Області", для первого запуска
    last_address = None
    ui.returnButton.setEnabled(False)
    branch_display = []  # Список для хранения и отображения текущей ветки

    def load_index(index: QtCore.QModelIndex):  # Функция для получения id нужного адреса
        nonlocal current_address
        nonlocal last_address
        address_id = index.siblingAtColumn(1).data(QtCore.Qt.ItemDataRole.DisplayRole)
        last_address = current_address  # Присвоение старого адреса к новой переменной
        current_address = branch[last_address]["next_step"]  # Назначение нового адреса как текущего
        branch[current_address]["f_key"] = address_id  # Назначение внешнего ключа к новому адресу
        ui.address_lookup.clear()  # Очистка поля для поиска
        addressTable()  # Заполнение таблицы

    """Словарь для хранения значений нужных для хождения по ветке адресов"""
    branch = {
        "Regions": {
            "type_name": "Області",
            "f_key": None,
            "last_step": None,
            "next_step": "Districts",
            "DB_table": ["region_name", "regions", "region_id"]
        },
        "Districts": {
            "type_name": "Райони",
            "f_key": None,
            "last_step": "Regions",
            "next_step": "Localities",
            "DB_table": ["district_name", "districts", "district_id"]
        },
        "Localities": {
            "type_name": "Н.п.",
            "f_key": None,
            "last_step": "Districts",
            "next_step": "Streets",
            "DB_table": ["locality_name", "localities", "locality_id"]
        },
        "Streets": {
            "type_name": "Вулиці",
            "f_key": None,
            "last_step": "Localities",
            "next_step": "H_Numbers",
            "DB_table": ["street_name", "streets", "streets_id"]
        },
        "H_Numbers": {
            "type_name": "Будівлі",
            "f_key": None,
            "last_step": "Streets",
            "next_step": None,
            "DB_table": ["house_number", "house_numbers", "house_number_id"]
        }
    }

    def sql_request(column, table, id_column, id):  # SQL запрос, который зависит от типа адреса на котором мы находимся
        if table == "regions":  # SQL запрос если мы на таблице областей
            cursor.execute(
                f"select {column}, {id_column} from {table} where {column} like '%{ui.address_lookup.text()}%'")
            result = cursor.fetchall()
        else:  # SQL запрос если мы на любой другой таблице
            last_step = branch[current_address]["last_step"]
            cursor.execute(
                f"""select {column}, {id_column} from {table} where {column} like '%{ui.address_lookup.text()}%' 
                                                        AND {branch[last_step]["DB_table"][2]} = {id} """)
            result = cursor.fetchall()
        return result

    def check_connect(status=False):  # Функция для подключения и отключения функций к таблице адресов
        if status == "numb":  # Если мы на странице списка домов, то откл. двойного нажатия
            try:
                ui.tableWidget.doubleClicked.disconnect()
            except:
                pass
            try:
                ui.tableWidget.cellChanged.disconnect()
            except:
                pass
        if status and current_address != "H_Numbers":  # Если мы не на стр. списка домов и не в режиме ред. то откл. ред. ячеек таблици и подкл. дв. нажатия
            try:
                ui.tableWidget.cellChanged.disconnect()
            except:
                pass
            ui.tableWidget.doubleClicked.connect(load_index)
        elif not status:  # Если мы в режиме ред. то откл. дв. нажатия и подкл. ред. ячеек
            try:
                ui.tableWidget.doubleClicked.disconnect()
            except:
                pass
            ui.tableWidget.cellChanged.connect(update_row)

    def addressTable(id=None, return_b=False):  # Таблица с aдресами, заполнение зависит на каком мы сейчас типе адреса и от вида перехода(вперед по ветке или назад)
        nonlocal current_address

        def sql_tamlate():  # sql шаблон
            result = sql_request(
                branch[current_address]["DB_table"][0],
                branch[current_address]["DB_table"][1],
                branch[current_address]["DB_table"][2],
                branch[current_address]["f_key"]
            )
            return result

        if not return_b:  # SQL запрос при переходе дальше по ветке и при обновлении таблицы
            if branch[current_address]["type_name"] not in branch_display:
                branch_display.append(branch[current_address]["type_name"])
            result = sql_tamlate()
        else:  # SQL запрос при переходе по ветке на шаг назад
            branch_display.pop(-1)
            last_step = branch[current_address]["last_step"]  # Прошлый адрес
            current_address = last_step  # Назначение прошлого адреса текущим
            result = sql_tamlate()
            ui.address_lookup.clear()  # Очистка поля для поиска

        if current_address == "Regions":  # Если тип адреса "Області", то отключение кнопки возвращения
            ui.returnButton.setEnabled(False)
        else:
            ui.returnButton.setEnabled(True)

        check_connect("numb")  # Откл. двойного нажатия если мы на стр. списка домов и подкл. если мы не на ней

        ui.label_2.setText("->".join(branch_display))  # Вывод текущей ветки

        """Заполнение таблицы"""
        ui.tableWidget.setColumnCount(2)
        ui.tableWidget.setHorizontalHeaderLabels([f"{branch[current_address]['type_name']}", "id"])
        ui.tableWidget.setRowCount(len(result))

        for row, item in enumerate(result):
            ui.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(item[0])))
            ui.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(item[1])))

    old_row_count = 0

    def state_change(status=False):  # Смена режима с редактирования на просмотр и наоборот
        updated_rows.clear()  # Обнуление словаря обновленных строчек

        if status:  # Если переход в режим редактирования
            check_connect(False)
            ui.tableWidget.setEditTriggers(QTableWidget.AllEditTriggers)
            ui.editButton.setEnabled(False)
            ui.returnButton.setEnabled(False)
            ui.address_lookup.setEnabled(False)
            ui.cancelButton.setStyleSheet("background-color: rgb(255, 49, 52)")
        else:  # Если переход в режим просмотра
            check_connect(True)
            if not current_address != "Regions":
                ui.returnButton.setEnabled(True)

            ui.editButton.setEnabled(True)
            ui.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
            ui.cancelButton.setStyleSheet("background-color: rgb(255, 123, 123)")

        nonlocal old_row_count
        old_row_count = ui.tableWidget.rowCount()
        ui.addButton.setEnabled(status)
        ui.deleteButton.setEnabled(status)
        ui.saveButton.setEnabled(status)
        ui.cancelButton.setEnabled(status)

    updated_rows = {}

    def update_row():  # Запись id измененной строки и сам измененный текст в словарь
        id = ui.tableWidget.item(ui.tableWidget.currentRow(), 1).text()
        if id != "":
            updated_rows[id] = ui.tableWidget.item(ui.tableWidget.currentRow(), 0).text()

    def save_changes():  # Обновление, сохранение и удаление данных в БД
        ui.address_lookup.setEnabled(True)

        table = branch[current_address]["DB_table"][1]
        column = branch[current_address]["DB_table"][0]
        column_id = branch[current_address]["DB_table"][2]

        """Обновление отредактированных ячеек в БД"""
        for id, row in updated_rows.items():
            cursor.execute(
                f"""UPDATE {table} SET {column}='{row}' WHERE {column_id}={id}""")
            db.commit()

        """Удаление строчек в БД"""
        for id in deleted_rows:
            cursor.execute(
                f"""DELETE FROM {table} WHERE {column_id}={id}""")
            db.commit()

        """Добавление новых ячеек в БД"""
        if current_address == "Regions":  # SQL запрос на добавление новых строк в БД, если мы на странице областей
            for row in range(old_row_count, ui.tableWidget.rowCount()):
                cursor.execute(f"""INSERT INTO {table}({column})
                                                VALUES("{ui.tableWidget.item(row, 0).text()}")""")
                db.commit()
        else:  # SQL запрос на добавление новых строк в БД, если мы не на странице областей
            l_address = branch[current_address]["last_step"]
            f_key_column = branch[l_address]["DB_table"][2]

            for row in range(old_row_count, ui.tableWidget.rowCount()):
                cursor.execute(f"""INSERT INTO {table}({column}, {f_key_column})
                                                VALUES("{ui.tableWidget.item(row, 0).text()}",
                                                "{branch[current_address]["f_key"]}")""")
                db.commit()

        updated_rows.clear()
        deleted_rows.clear()

        state_change()
        addressTable()

    def add_new_row():  # Добавление новой строки в таблицу
        try:
            ui.tableWidget.cellChanged.disconnect()
        except:
            pass

        new_row_count = ui.tableWidget.rowCount()
        new_row_count += 1
        ui.tableWidget.setRowCount(new_row_count)
        ui.tableWidget.setItem(new_row_count - 1, 0, QtWidgets.QTableWidgetItem(""))
        ui.tableWidget.setItem(new_row_count - 1, 1, QtWidgets.QTableWidgetItem(""))
        ui.tableWidget.cellChanged.connect(update_row)

    deleted_rows = set()

    def del_new_row():  # Функция удаления строки
        row = ui.tableWidget.currentRow()
        if row > -1:  # Если есть выделенная строка/элемент
            if ui.tableWidget.item(row, 1).text() == "":  # Если мы удаляем только что созданную строку, то она просто удаляеться
                ui.tableWidget.removeRow(row)
                ui.tableWidget.selectionModel().clearCurrentIndex()  # этот вызов нужен для того, чтобы сбросить индекс выбранной строки
            else:  # Если мы удаляем строку которая есть в БД то она не пропадет а покрасится в серый и не удалится пока мы не нажмем сохранить
                if current_address == "H_Numbers":
                    ui.tableWidget.item(row, 0).setBackground(QtGui.QColor(192, 192, 192))
                    deleted_rows.add(ui.tableWidget.item(row, 1).text())
                    ui.tableWidget.selectionModel().clearCurrentIndex()  # этот вызов нужен для того, чтобы сбросить индекс выбранной строки
                else:  # Проверка есть ли у выбранной для удаления строки вложенные адреса
                    next_step = branch[current_address]["next_step"]
                    colum_f_key = branch[current_address]["DB_table"][2]
                    table = branch[next_step]["DB_table"][1]
                    f_key = ui.tableWidget.item(row, 1).text()
                    cursor.execute(
                        f"select * from {table} where {colum_f_key}='{f_key}'")
                    result = cursor.fetchall()
                    if result:  # Если есть, то вызов окна предупреждения
                        error_window(f"Помилка: в даній адресі є вкладені адреси, \nвидаліть їх спочатку", 1)
                    else:  # Если нет, то удаления из базы данных
                        ui.tableWidget.item(row, 0).setBackground(QtGui.QColor(192, 192, 192))
                        deleted_rows.add(ui.tableWidget.item(row, 1).text())
                        ui.tableWidget.selectionModel().clearCurrentIndex()

    def cancel_changes():
        ui.address_lookup.setEnabled(True)
        updated_rows.clear()
        deleted_rows.clear()
        state_change()
        addressTable()

    ui.tableWidget.verticalHeader().setVisible(False)  # Отключение нумерации таблицы
    state_change()  # Установка в первом запуске режим просмотра
    ui.cancelButton.clicked.connect(cancel_changes)  # Кнопка отмены изменений
    ui.addButton.clicked.connect(add_new_row)  # Кнопка добавления новой строки
    ui.deleteButton.clicked.connect(del_new_row)  # Кнопка удаления строки
    ui.saveButton.clicked.connect(save_changes)  # Кнопка сохранения измененных, добавленных и удаленных строк
    ui.editButton.clicked.connect(lambda sh, status=True: state_change(status))  # Кнопка перехода в режим редактирования
    addressTable()  # Первое заполнение таблицы
    ui.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)  # Отключение редактирования ячеек таблицы
    ui.tableWidget.hideColumn(1)  # Скрытие колонки с id адресов
    ui.address_lookup.textChanged.connect(lambda sh, id=branch[current_address]["f_key"]: addressTable(id))  # Заполнение таблицы при смене текста в ячейке для поиска адресса
    ui.returnButton.clicked.connect(lambda sh, id=None, ret=True: addressTable(id, ret))  # Кнопка возвращения на пред. шаг
    ui.tableWidget.doubleClicked.connect(load_index)  # Переход на список след. тип адреса выбраного адреса двойным нажатием мышки


def error_window(text, error_type, id=""):
    global errorWindow
    errorWindow = QtWidgets.QDialog()
    ui = Ui_errorWindow()
    ui.setupUi(errorWindow)
    errorWindow.show()

    ui.label.setText(text)

    def close_window():
        if error_type == 1:
            errorWindow.close()
        elif error_type == 2:
            entering_additional_information(id)
            errorWindow.close()
        elif error_type == 3:
            entering_additional_information_file(id)
            errorWindow.close()
        elif error_type == 4:
            deleting_patients_diagnosis()
            errorWindow.close()
        else:
            errorWindow.close()

    ui.pushButton.clicked.connect(close_window)


def katalog():  # Главная окно со списком карточек
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    def updateTable(sql_search=False):  # таблица со списком карточек пациентов
        if not sql_search:
            """SQL запрос на инф. из 4 столбцов для добавления в виджет без фильтров"""
            cursor.execute("SELECT cards_id, region, district, locality, street_type, street, house_numb FROM cards")
            result = cursor.fetchall()
        else:
            """SQL запрос с фильтрами"""
            cursor.execute(
                f"""SELECT cards_id, region, district, locality, street_type, street, house_numb FROM cards join diagnoses using(cards_id)
                                WHERE street LIKE '%{ui.search_street.text()}%' AND house_numb LIKE '%{ui.search_house.text()}%' 
                                AND patient_name LIKE '%{ui.search_patient.text()}%' AND manager LIKE '%{ui.search_manager.text()}%'
                                GROUP BY cards_id""")
            result = cursor.fetchall()
            print(result)

        """Заполнение таблицы"""
        ui.tableWidget.setRowCount(len(result))
        for row, items in enumerate(result[::-1]):
            for index, item in enumerate(items):
                item = str(item)
                if item.isnumeric():
                    ui.tableWidget.setItem(row, index, QtWidgets.QTableWidgetItem((' ' * 9 + str(item))[-9:]))
                else:
                    ui.tableWidget.setItem(row, index, QtWidgets.QTableWidgetItem(str(item)))

            """Создание и добавление кнопки в таблицу на открытие карточки пациента"""
            button = QtWidgets.QPushButton('Перегляд')
            button.clicked.connect(lambda sh, id=items[0]: otherWindow_2(id))
            ui.tableWidget.setCellWidget(row, 7, button)
        ui.tableWidget.setSortingEnabled(False)
        ui.sortButton.setEnabled(True)

    def sort_table():  # Сортировка столбцов
        ui.tableWidget.setSortingEnabled(True)
        ui.sortButton.setEnabled(False)

    updateTable()

    def load_info_from_file():  # Загрузка из файла типа json всех данных и добавление их в ячейки
        fname = QFileDialog().getOpenFileName(MainWindow, "Open", "save_cards", "Карточки формата json (*.json)")

        if fname[0]:
            with open(f"{fname[0]}", "r") as out_file:
                data = json.load(out_file)
                otherWindow_3(data)

    ui.tableWidget.verticalHeader().setVisible(False)  # Отключение нумерации таблицы
    ui.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)  # Отключение редакта ячеек таблицы
    ui.address_listsButton.clicked.connect(address_lists)  # Кнопка для просмотра адрес сов
    ui.view_fileButton.clicked.connect(load_info_from_file)  # Кнопка для просмотра файла
    ui.sortButton.clicked.connect(sort_table)  # Кнопка сортировки столбцов
    ui.updateButton.clicked.connect(updateTable)  # Кнопка обновление таблицы
    ui.pushButton.clicked.connect(otherWindow)  # Подключение к кнопке открытие нового окна на добавление новой карточки
    ui.searchButton.clicked.connect(lambda sh, sql_search=True: updateTable(sql_search))  # Кнопка для поиска пациента

    sys.exit(app.exec())


if __name__ == '__main__':

    if "katalog.exe" in sys.argv[0]:
        path = sys.argv[0][:-12]
    else:
        path = sys.argv[0][:-8]

    # path = "\\".join(sys.argv[0].split("\\")[:-1])

    with closing(sqlite3.connect(f"{path}\\data_bases\\data.db")) as db:
        cursor = db.cursor()

        if len(sys.argv) > 1:
            file = sys.argv[1]

            with open(f"{file}", "r") as out_file:
                data = json.load(out_file)
                app = QtWidgets.QApplication(sys.argv)
                otherWindow_3(data)
                sys.exit(app.exec())
        else:
            katalog()
