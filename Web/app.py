from flask import Flask, render_template, request, jsonify, session
from flask_session import Session

import numpy as np
from flask_socketio import SocketIO, send
from engineio.payload import Payload

from modelo import BaseMovil
from simulacion2 import MobileBasePID
from werkzeug.exceptions import abort

import threading

import sqlite3
from flask import Flask, render_template, url_for, flash, redirect

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user(id_user):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usuarios WHERE id = ?',
                        (id_user,)).fetchone()
    conn.close()
    if user is None:
        abort(404)
    return user

def get_changes(user, form):
    new = {}
    for x in form.keys():
        print(x)
        if x == "major":
            if form[x] == "robotica":
                new['robotica'] = 1
            else:
                new['robotica'] = 0
        elif form[x]:
            new[x] = form[x]
        else:
            new[x] = user[x]
    return new
       

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


Payload.max_decode_packets = 500
socketio = SocketIO(app, cors_allowed_origins='*')

ref = np.array([100.0, 100.0])

kp_l = 0.01
ki_l = 0.0
kd_l = 0.0
kp_a = 1.0
ki_a = 0.0
kd_a = 0.0

botin = BaseMovil()
cont = MobileBasePID(botin, ref, kp_l, kd_l, ki_l, kp_a, kd_a, ki_a)

@app.route("/")
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()
    return render_template("inicio/pagina_inicio.html", users = users)

@app.route("/main")
def main():
    return render_template("pagina_principal/info_lab.html")

@app.route("/login", methods = ['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        mail = request.form['email']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE mail = ?',
                        (mail,)).fetchone()
        conn.close()
        if user is None:
            error = 'Correo no registrado'
        else:
            if user['password'] == request.form["password"]:
                session['user_id'] = user["id"]
                return redirect("/main")
            else:
                error = 'Contraseña incorrecta'
    return render_template("login/index.html", error = error)

@app.route("/exp")
def exper():
    conn = get_db_connection()
    exp = conn.execute('SELECT * FROM experiencias WHERE id = ?',
                        (1,)).fetchone()
    conn.close()
    return render_template("pagina_exp/exp.html", exp = exp)

@app.route("/reg", methods=('GET', 'POST'))
def reg():
    if request.method == 'POST':
        uni = request.form['inst']
        if (uni == "UC" and request.form['carrera'] == "ing"):
            is_robot = int((request.form['major'] == 'robotica'))
        else:
            is_robot = 0
        conn = get_db_connection()
        conn.execute("INSERT INTO usuarios (name, lastname, mail, password, tipo, inst, carrera, robotica) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (request.form['name'], request.form['lastname'], request.form['email'],
             request.form['psw'], request.form['cargo'], uni, request.form["carrera"], is_robot))
        conn.commit()
        user = conn.execute('SELECT * FROM usuarios WHERE mail = ?',
                        (request.form['email'],)).fetchone()
        conn.close()
        session['user_id'] = user["id"]
        return redirect(url_for('main'))

    return render_template("registro/main.html")

@app.route("/res", methods =('GET', 'POST'))
def res():
    user_id = session["user_id"]

    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('INSERT INTO reservas (id_user, id_exp, fecha) VALUES (?, ?, ?))',
         (user_id, request.form['id_exp'], request.form['fecha']))
        conn.commit()
        conn.close()
        return redirect(url_for('exps'))

    return render_template("reserva_horas/reserva.html")

@app.route("/sim")
def sim():
    return render_template("Simulacion/simulacion_base_movil.html")

@app.route("/cuenta", methods=('GET', 'POST'))
def perfil():
    user = get_user(session["user_id"])

    if request.method == 'POST':
        new = get_changes(user, request.form)
        conn = get_db_connection()
        conn.execute('UPDATE usuarios SET name = ?, lastname = ?, mail = ?,'
         ' tipo = ?, inst = ?, carrera = ?, robotica = ? WHERE mail = ?',
         (new['name'], new['lastname'], new['mail'], new['tipo'], new['inst'], new['carrera'], new['robotica'], user['mail']))
        conn.commit()
        conn.close()
        return redirect(url_for('main'))

    return render_template("perfil/datos_personales.html", user = user)

@app.route("/sim/run")
def sim_run():
    def run_simulation():
        print("Corriendo Sim")
        botin.SetState([0,0,0,0,0])
        while(1):
            cont.update()
            botin.UpdateState()

    # botin.SetActuator([1.0, 0.5])
    
    simulation = threading.Thread(target=run_simulation)
    simulation.start()
    return render_template("Simulacion/simulacion_base_movil.html")

@app.route("/setGoal/<x>/<y>")
def set_goal(x,y):
    if request.method == 'GET':
        x = float(x)
        y = float(y)
        cont.set_reference(x,y)
        message = f'Goal set in ({x},{y})'
        return jsonify(message)  # serialize and use JSON headers
    # POST request
    if request.method == 'POST':
        print(request.get_json())  # parse as JSON
        return 'Sucesss', 200
    

@socketio.on('update')
def handleMessage(msg):
    # print("Enviando Mensaje")
    state = botin.GetSensor()
    state_dict = {
        'x': state[0], 
        'y': state[1],
        'theta': state[2]
    }
    send(state_dict, broadcast=True)

@app.route("/cuenta/exp")
def exps():
    user_id = session["user_id"]
    conn = get_db_connection()
    reservas = conn.execute('SELECT * FROM reservas WHERE id_user = ?',
                        (id_user,)).fetchAll()
    conn.close()
    return render_template("perfil/historial_experiencias.html", reservas)

@app.route("/cuenta/del", methods =('POST', ))
def delete():
    id_user = session.get("user_id")
    usuario = get_user(id_user)
    conn = get_db_connection()
    conn.execute('DELETE FROM usuarios WHERE id = ?', (id_user,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(usuario['name']))
    return redirect(url_for('index'))

@app.route("/salir", methods =('POST',))
def salir():
    session['user_id'] = None
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


