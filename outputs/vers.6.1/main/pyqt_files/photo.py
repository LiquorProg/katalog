# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'photo.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_photo(object):
    def setupUi(self, photo):
        photo.setObjectName("photo")
        photo.resize(383, 289)
        self.gridLayout = QtWidgets.QGridLayout(photo)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(photo)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(photo)
        QtCore.QMetaObject.connectSlotsByName(photo)

    def retranslateUi(self, photo):
        _translate = QtCore.QCoreApplication.translate
        photo.setWindowTitle(_translate("photo", "Dialog"))
        self.label.setText(_translate("photo", "TextLabel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    photo = QtWidgets.QDialog()
    ui = Ui_photo()
    ui.setupUi(photo)
    photo.show()
    sys.exit(app.exec_())
