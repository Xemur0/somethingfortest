import sqlite3

with sqlite3.connect('DBforTG.sqlite') as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS clients(
    name TEXT, 
    date DATE
    )""")