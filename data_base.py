import sqlite3
import sys


db = sqlite3.connect('data_bases/data.db')
cursor = db.cursor()

cursor.execute("""select * from patients""")
db.commit()
