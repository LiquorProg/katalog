import sys
from PyQt5.QtSql import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def createDB():
   db = QSqlDatabase.addDatabase('QSQLITE')
   db.setDatabaseName('data_bases/data.db')

   if not db.open():
      msg = QMessageBox()
      msg.setIcon(QMessageBox.Critical)
      msg.setText("Error in Database Creation")
      retval = msg.exec_()
      return False
   query = QSqlQuery()

   query.exec_("insert into patients (full_name, age, info, street, affiliation, mobile_1, house_numb)  values(sasha, 23, adawdawd, dawdaw, dada, 888888, 8)")
   query.exec_("insert into sportsmen values(106, 'Авффцв', 'вфцвфц')")

   return True

if __name__ == '__main__':
   app = QApplication(sys.argv)
   createDB()