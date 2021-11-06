import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO usuarios (name, lastname, mail, password, tipo, inst, carrera, robotica) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ('Admin', 'Istrador', 'admin@gmail.com', 'admin1', 'admin', 'PUC', 'ing', 1)
            )
desc = 'En esta experiencia aprenderás sobre el control PID y como usar este para controlar un robot de dos ruedas para llegar a un punto especifico de forma precisa y correcta.'

cur.execute("INSERT INTO experiencias (nombre, duracion, tipo, descripcion) VALUES (?, ?, ?, ?)",
            ('Robot PID', 30, 'control', desc)
            )

connection.commit()
connection.close()