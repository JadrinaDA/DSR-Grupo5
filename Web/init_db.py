import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO usuarios (name, lastname, mail, password, tipo, inst, carrera, robotica) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ('Admin', 'Istrador', 'admin@gmail.com', 'admin1', 'admin', 'PUC', 'ing', 1)
            )

connection.commit()
connection.close()