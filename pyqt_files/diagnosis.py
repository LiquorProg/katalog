# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyqt_files\diagnosis.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_add_diag(object):
    def setupUi(self, Dialog_add_diag):
        Dialog_add_diag.setObjectName("Dialog_add_diag")
        Dialog_add_diag.resize(541, 238)
        Dialog_add_diag.setMinimumSize(QtCore.QSize(0, 0))
        self.formLayout_2 = QtWidgets.QFormLayout(Dialog_add_diag)
        self.formLayout_2.setObjectName("formLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(-1, -1, -1, 0)
        self.gridLayout.setHorizontalSpacing(4)
        self.gridLayout.setObjectName("gridLayout")
        self.apart_add_diag = QtWidgets.QLineEdit(Dialog_add_diag)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.apart_add_diag.sizePolicy().hasHeightForWidth())
        self.apart_add_diag.setSizePolicy(sizePolicy)
        self.apart_add_diag.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.apart_add_diag.setFont(font)
        self.apart_add_diag.setMaxLength(10)
        self.apart_add_diag.setObjectName("apart_add_diag")
        self.gridLayout.addWidget(self.apart_add_diag, 1, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(Dialog_add_diag)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_10.setFont(font)
        self.label_10.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_10.setStyleSheet("")
        self.label_10.setTextFormat(QtCore.Qt.PlainText)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 0, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(Dialog_add_diag)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_12.setFont(font)
        self.label_12.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_12.setTextFormat(QtCore.Qt.PlainText)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 2, 0, 1, 1)
        self.patient_add_diag = QtWidgets.QLineEdit(Dialog_add_diag)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.patient_add_diag.sizePolicy().hasHeightForWidth())
        self.patient_add_diag.setSizePolicy(sizePolicy)
        self.patient_add_diag.setMinimumSize(QtCore.QSize(200, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.patient_add_diag.setFont(font)
        self.patient_add_diag.setMaxLength(30)
        self.patient_add_diag.setObjectName("patient_add_diag")
        self.gridLayout.addWidget(self.patient_add_diag, 2, 1, 1, 1)
        self.dateEdit_add_diag = QtWidgets.QDateEdit(Dialog_add_diag)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dateEdit_add_diag.sizePolicy().hasHeightForWidth())
        self.dateEdit_add_diag.setSizePolicy(sizePolicy)
        self.dateEdit_add_diag.setMinimumSize(QtCore.QSize(142, 0))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dateEdit_add_diag.setFont(font)
        self.dateEdit_add_diag.setDate(QtCore.QDate(2023, 1, 1))
        self.dateEdit_add_diag.setObjectName("dateEdit_add_diag")
        self.gridLayout.addWidget(self.dateEdit_add_diag, 0, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(Dialog_add_diag)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_11.setFont(font)
        self.label_11.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_11.setTextFormat(QtCore.Qt.PlainText)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 1, 0, 1, 1)
        self.formLayout_2.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.gridLayout)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_13 = QtWidgets.QLabel(Dialog_add_diag)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_13.setFont(font)
        self.label_13.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_13.setTextFormat(QtCore.Qt.PlainText)
        self.label_13.setObjectName("label_13")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_13)
        self.diagnosis_add_diag = QtWidgets.QTextEdit(Dialog_add_diag)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.diagnosis_add_diag.setFont(font)
        self.diagnosis_add_diag.setObjectName("diagnosis_add_diag")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.diagnosis_add_diag)
        self.formLayout_2.setLayout(1, QtWidgets.QFormLayout.SpanningRole, self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(390, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.formLayout_2.setItem(2, QtWidgets.QFormLayout.LabelRole, spacerItem)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.add_to_table_Button = QtWidgets.QPushButton(Dialog_add_diag)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_to_table_Button.sizePolicy().hasHeightForWidth())
        self.add_to_table_Button.setSizePolicy(sizePolicy)
        self.add_to_table_Button.setMinimumSize(QtCore.QSize(100, 0))
        self.add_to_table_Button.setMaximumSize(QtCore.QSize(100, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.add_to_table_Button.setFont(font)
        self.add_to_table_Button.setObjectName("add_to_table_Button")
        self.gridLayout_3.addWidget(self.add_to_table_Button, 0, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem1, 0, 0, 1, 1)
        self.formLayout_2.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.gridLayout_3)

        self.retranslateUi(Dialog_add_diag)
        QtCore.QMetaObject.connectSlotsByName(Dialog_add_diag)

    def retranslateUi(self, Dialog_add_diag):
        _translate = QtCore.QCoreApplication.translate
        Dialog_add_diag.setWindowTitle(_translate("Dialog_add_diag", "Новий діагноз"))
        self.label_10.setText(_translate("Dialog_add_diag", "Дата"))
        self.label_12.setText(_translate("Dialog_add_diag", "Пацієнт"))
        self.label_11.setText(_translate("Dialog_add_diag", "кв."))
        self.label_13.setText(_translate("Dialog_add_diag", "Діагноз"))
        self.add_to_table_Button.setText(_translate("Dialog_add_diag", "Додати"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_add_diag = QtWidgets.QDialog()
    ui = Ui_Dialog_add_diag()
    ui.setupUi(Dialog_add_diag)
    Dialog_add_diag.show()
    sys.exit(app.exec_())
