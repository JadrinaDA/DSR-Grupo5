import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO usuarios (name, mail, password, tipo, robotica) VALUES (?, ?, ?, ?, ?)",
            ('Admin', 'admin@gmail.com', 'admin1', 'admin', 1)
            )

connection.commit()
connection.close()