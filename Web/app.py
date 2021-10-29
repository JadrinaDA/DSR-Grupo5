from flask import Flask, render_template, request, jsonify

import numpy as np
from flask_socketio import SocketIO, send
from engineio.payload import Payload

from modelo import BaseMovil
from simulacion2 import MobileBasePID

import threading

import sqlite3
from flask import Flask, render_template, url_for, flash, redirect

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
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

@app.route("/login")
def login():
    return render_template("login/index.html")

@app.route("/exp")
def exper():
    return render_template("pagina_exp/exp.html")

@app.route("/reg", methods=('GET', 'POST'))
def reg():
    if request.method == 'POST':
        is_robot = 0 #int((request.form['major'] == 'rob'))
        name = request.form['name'] + " " + request.form['last_name'] 
        conn = get_db_connection()
        conn.execute("INSERT INTO usuarios (name, mail, password, tipo, robotica) VALUES (?, ?, ?, ?, ?)",
            (name, request.form['email'],
             request.form['psw'], 'alumno', is_robot))
        conn.commit()
        conn.close()
        return redirect(url_for('main'))

    return render_template("registro/main.html")

@app.route("/res")
def res():
    return render_template("reserva_horas/reserva.html")

@app.route("/sim")
def sim():
    return render_template("Simulacion/simulacion_base_movil.html")

@app.route("/cuenta")
def perfil():
    return render_template("perfil/datos_personales.html")

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
    return render_template("perfil/historial_experiencias.html")

if __name__ == '__main__':
    app.run(debug=True)


